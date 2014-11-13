#!/usr/bin/env python

import webapp2
import jinja2
import os
import json
import logging
import datetime
import cgi

import xml.etree.ElementTree as ET

import error_handlers as errors
import models

from google.appengine.api import urlfetch

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.loopcontrols'])


class MapViewHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/map.html')
        self.response.write(template.render())

class MapDataHandler(webapp2.RequestHandler):

    def get(self):

        # get an prepare all points
        locations = models.GeoPosition.all()
        locations.order('timestamp')
        points = []
        for point in locations.run():
            points.append({
                'name': point.name,
                'description': point.description,
                'timestamp': point.timestamp.strftime("%d.%m.%Y um %H:%M:%S UTC"),
                'longitude': point.longitude,
                'latitude': point.latitude,
            })

        # get and prepare all lines
        connectors = models.GeoLine.all()
        lines = []
        for line in connectors.run():
            lines.append({
                'start_longitude': line.start_longitude,
                'start_latitude': line.start_latitude,
                'end_longitude': line.end_longitude,
                'end_latitude': line.end_latitude,
            })

        data = {
            'points': points,
            'lines': lines,
        }
        self.response.write(json.dumps(data))


class MapUpdateHandler(webapp2.RequestHandler):

    def get(self):

        # get the data from robert
        result = urlfetch.fetch("http://home.arcor.de/robert_r/aust.kml")
        if (result.status_code != 200):
            logging.error("Error: {}\nMessage: {}".format(result.status_code, result.content))
            self.response.set_status(500)
            return

        # parse the data and store it in the datastore
        kml = ET.fromstring(result.content)
        #kml = ET.parse('test.kml')
        kml_data = kml.find('./{http://www.opengis.net/kml/2.2}Document')

        try:
            # add all new points
            for point in kml_data.findall('./{http://www.opengis.net/kml/2.2}Placemark'):
                name = point.find('./{http://www.opengis.net/kml/2.2}name').text
                description = point.find('./{http://www.opengis.net/kml/2.2}description').text
                coordinates = point.find('./{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates').text.split(',')
                longitude = coordinates[0]
                latitude = coordinates[1]
                timestamp_text = point.find('./{http://www.opengis.net/kml/2.2}TimeStamp/{http://www.opengis.net/kml/2.2}when').text
                try :
                    timestamp = datetime.datetime.strptime(timestamp_text, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    timestamp_text = timestamp_text[:len(timestamp_text) - 6]
                    timestamp = datetime.datetime.strptime(timestamp_text, "%Y-%m-%dT%H:%M:%S")
                except:
                    logging.error("kml file not correct:\n{}".format(kml))
                    self.response.set_status(500)
                    return

                # check whether point already present in database
                query = models.GeoPosition.all()
                query.filter('latitude =', latitude)
                query.filter('longitude = ', longitude)
                if query.count() == 0:
                    # it is not in the database and we have to add it
                    new_position = models.GeoPosition(
                        name=cgi.escape(name),
                        description=cgi.escape(description),
                        timestamp=timestamp,
                        longitude=cgi.escape(longitude),
                        latitude=cgi.escape(latitude),)
                    new_position.put()
                else:
                    # if it is there check whether the description has changed
                    position = query.get()
                    description = cgi.escape(description)
                    if position.description != description:
                        position.description = description
                    name = cgi.escape(name)
                    if position.name != name:
                        position.name = name
                    position.put()

        except AttributeError:
            logging.error("kml file not correct:\n{}".format(kml))
            self.response.set_status(500)
            return

        try:
            folder = kml_data.find('./{http://www.opengis.net/kml/2.2}Folder')
            if (folder.find('./{http://www.opengis.net/kml/2.2}name').text != 'Lines'):
                logging.warning('no lines in kml file')
                return
            
            # add all new lines
            for line in folder.findall('./{http://www.opengis.net/kml/2.2}Placemark'):
                coordinates = line.find('./{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates').text.split(' ')
                
                start = coordinates[0].split(',')
                start_longitude = start[0]
                start_latitude = start[1]
                
                end = coordinates[1].split(',')
                end_longitude = end[0]
                end_latitude = end[1]

                query = models.GeoLine.all()
                query.filter('start_longitude =', start_longitude)
                query.filter('start_latitude =', start_latitude)
                query.filter('end_latitude =', end_latitude)
                query.filter('end_longitude =', end_longitude)

                if query.count() == 0:
                    new_line = models.GeoLine(
                        start_latitude=cgi.escape(start_latitude),
                        start_longitude=cgi.escape(start_longitude),
                        end_latitude=cgi.escape(end_latitude),
                        end_longitude=cgi.escape(end_longitude), )
                    new_line.put()
        except AttributeError:
            logging.error("kml file not correct:\n{}".format(kml))
            self.response.set_status(500)
            return
        


HANDLERS = [
    ('/map', MapViewHandler),
    ('/map/data', MapDataHandler),
    ('/map/update', MapUpdateHandler),
]

app = webapp2.WSGIApplication(HANDLERS, debug=False)

app.error_handlers[404] = errors.handle_404
#app.error_handlers[500] = errors.handle_500
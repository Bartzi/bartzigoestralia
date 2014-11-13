#!/usr/bin/env python

from __future__ import unicode_literals

import webapp2
import jinja2

class WriteHandler(webapp2.RequestHandler):

    def get(self):
        return 'Hallo'


HANDLERS = [
    ('/write', MainHandler),
]
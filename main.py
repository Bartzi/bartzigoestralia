#!/usr/bin/env python

#from __future__ import unicode_literals

import webapp2
import jinja2
import os
import datetime
import cgi
import pytz

import error_handlers as errors
import models
import logging

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.api import mail



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.loopcontrols'])

def format_datetime(value):
    if value is None:
        return "long ago..."
    return value.strftime("%d.%m.%y um %H:%M UTC")

def format_datetime_comment(date):
    if date is None:
        return "long ago..."
    return date.strftime("%d.%m/%H:%M UTC")

JINJA_ENVIRONMENT.filters['datetime'] = format_datetime
JINJA_ENVIRONMENT.filters['datetime_comment'] = format_datetime_comment

TIMEZONE = pytz.timezone('UTC')


def addInfo(handler):
    try:
        css_name = handler.request.cookies['css']
    except KeyError:
        css_name = 'lara'
    user = users.get_current_user()
    args = {
        'css': "{name}.css".format(name=css_name),
    }
    if user: 
            args['logout'] = users.create_logout_url('/overview')
            args['username'] = user.nickname()
    return args


class MainHandler(webapp2.RequestHandler):

    def get(self):
        expiration_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
        self.response.set_cookie('css', 'normal_background', expires=expiration_date)
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        css = {'css': 'normal_background.css'}
        self.response.write(template.render(css))


class LaraHandler(webapp2.RequestHandler):

    def get(self):
        expiration_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
        self.response.set_cookie('css', 'lara', expires=expiration_date)
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        css = {'css': 'lara.css'}
        self.response.write(template.render(css))


class OverviewHandler(webapp2.RequestHandler):

    def get(self):
        query = models.Post.all()
        query.order('-date')
        posts = []
        post_count = 0
        for post in query.run():
            if post_count > 2:
                break
            posts.append(post)
            post_count += 1
        template = JINJA_ENVIRONMENT.get_template('templates/overview.html')
        args = addInfo(self)
        args['posts'] = posts
        self.response.write(template.render(args))

class MorePostsHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/more_posts.html')
        query = models.Post.all()
        query.order('-date')
        posts = []
        post_count = 0
        last_post_seen = False;
        last_post = self.request.get('last_post')
        overall_post_count = 0
        for post in query.run():
            logging.info(overall_post_count)
            if overall_post_count >= 9:
                self.response.write("nothing")
                return
            if post_count > 2 :
                break
            if last_post_seen:
                posts.append(post)
                post_count += 1
            if str(post.key()) == last_post:
                last_post_seen = True
            overall_post_count += 1
        #return self.response.write(posts)
        args = { 'posts': posts }
        self.response.write(template.render(args))



class CommentHandler(webapp2.RequestHandler):

    def post(self):
        user = cgi.escape(self.request.get("name"))
        comment = cgi.escape(self.request.get("comment"))
        post_id = cgi.escape(self.request.get("id"))
        post = models.Post.get(post_id)
        comment_entity = models.Comment(name=user, content=comment, post=post, date=datetime.datetime.now(pytz.utc))
        comment_entity.put()
        sender = "informer@bartzigoestralia.appspotmail.com"
        subject = "new comment"
        body = unicode("Hi,\n{name} wrote this comment:\n{comment}\nfor the post:\n{post}""".format(
            name=user.encode('ascii', 'ignore'),
            comment=comment.encode('ascii', 'ignore'),
            post=post.title.encode('ascii', 'ignore')))
        mail.send_mail(sender, "christian.bartz@bartzigoestralia.de", subject, body)
        self.response.write(post)

class PostHandler(webapp2.RequestHandler):

    def post(self):
        #try:
        user = cgi.escape(self.request.get("name"))
        title = cgi.escape(self.request.get("title"))
        content = self.request.get("content")
        post = models.Post(title=title, content=content, author=user, date=datetime.datetime.now(pytz.utc))
        post.put()
        self.response.write("Success!")
        #except:
        #    self.response.write("Hmm Something went wrong =(")

class WriteHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/write.html')
        args = addInfo(self)
        self.response.write(template.render(args))

class EditHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/edit_post.html')
        args = addInfo(self)
        query = models.Post.all()
        query.order('-date')
        posts = []
        for post in query.run():
            posts.append(post)
        args['posts'] = posts
        self.response.write(template.render(args))

class EditPostHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/post_edit.html')
        post_id = self.request.get('post_id');
        post = models.Post.get(post_id)
        args = {'post': post}
        self.response.write(template.render(args))

class ExchangePostDataHandler(webapp2.RequestHandler):

    def post(self):
        id = self.request.get('post_id')
        if (id):
            post = models.Post.get(id)
            title = self.request.get('title')
            if title:
                post.title = title
            else:
                post.content = self.request.get('content')
            post.put()
            return self.response.write("saved Post")
        id = self.request.get('image_id')
        image = models.Image.get(id)
        image.name = self.request.get('name')
        image.put()
        self.response.write("saved image {}".format(image.name))

class ImageHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self):
        image_key = self.request.get('img_id')
        blob = blobstore.BlobInfo.get(image_key)
        #return self.response.write(blob)
        if image_key:
            self.send_blob(blob)
        else:
            self.error(404)


class ImagePostHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self):
        uploads = self.get_uploads()
        name = cgi.escape(self.request.get("name"))
        if not name:
            name = "no description"
        post = db.get(self.request.get("post_id"))
        for upload in uploads:
            image = models.Image(data=upload, name=name, post=post)
            image.put()
        self.redirect('/write')


class ImageForm(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/image_upload.html')
        args = addInfo(self)
        posts = models.Post.all()
        posts.order('-date')
        args["upload_url"] = blobstore.create_upload_url('/upload')
        args["posts"] = posts
        self.response.write(template.render(args))


class ArchiveHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/archive.html')
        args = addInfo(self)
        query = models.Post.all()
        query.order('-date')
        posts = []
        for post in query.run():
            posts.append(post)
        args["posts"] = posts
        self.response.write(template.render(args))


class PostViewHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/view_post.html')
        post = db.get(self.request.get('post_id'))
        args = addInfo(self)
        args['post'] = post
        self.response.write(template.render(args))






def handle_404(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('default_error.html')
    error_code = {"code": "404"}
    response.write(template.render(error_code))

HANDLERS = [
    ('/', MainHandler),
    ('/lara', LaraHandler),
    ('/overview', OverviewHandler),
    ('/addcomment', CommentHandler),
    ('/addPost', PostHandler),
    ('/write', WriteHandler),
    ('/edit', EditHandler),
    ('/addImage', ImageForm),
    ('/img', ImageHandler),
    ('/upload', ImagePostHandler),
    ('/more', MorePostsHandler),
    ('/postdata', EditPostHandler),
    ('/changepost', ExchangePostDataHandler),
    ('/archive', ArchiveHandler),
    ('/viewpost', PostViewHandler),
]

app = webapp2.WSGIApplication(HANDLERS, debug=False)

app.error_handlers[404] = errors.handle_404
app.error_handlers[500] = errors.handle_500

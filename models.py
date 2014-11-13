from google.appengine.ext import db
from google.appengine.ext import blobstore


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    tags = db.StringListProperty()
    date = db.DateTimeProperty(required=True)
    images = db.StringListProperty()

    def add_image(self, id):
        self.images.append(id)
    
class Comment(db.Model):
    post = db.ReferenceProperty(Post)
    name = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    date = db.DateTimeProperty()


class Image(db.Model):
    name = db.StringProperty(required=True)
    data = blobstore.BlobReferenceProperty(required=True)
    post = db.ReferenceProperty(Post)


class GeoPosition(db.Model):

    name = db.TextProperty()
    description = db.TextProperty()
    longitude = db.StringProperty()
    latitude = db.StringProperty()
    timestamp = db.DateTimeProperty()

class GeoLine(db.Model):

    start_longitude = db.StringProperty()
    start_latitude = db.StringProperty()
    end_longitude = db.StringProperty()
    end_latitude = db.StringProperty()

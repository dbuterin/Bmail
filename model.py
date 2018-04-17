from google.appengine.ext import ndb

class Message(ndb.Model):
    message = ndb.StringProperty()
    sender = ndb.StringProperty()
    receiver = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
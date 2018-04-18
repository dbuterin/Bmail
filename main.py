#!/usr/bin/env python
import os
import jinja2
import webapp2
import json
from google.appengine.api import users
from google.appengine.api import urlfetch
from model import Message


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))
class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            prijavljen = True
            logout_url = users.create_logout_url('/')
            params = {"prijavljen": prijavljen, "logout_url": logout_url, "user": user}
            return self.render_template("hello.html", params=params)
        else:
            prijavljen = False
            login_url = users.create_login_url('/')
            params = {"prijavljen": prijavljen, "login_url": login_url, "user": user}
            return self.render_template("hello.html", params=params)
class AllMessagesHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            prijavljen = True
            messages = Message.query().fetch()
            params = {"messages": messages}
            params["user"] = user
            logout_url = users.create_logout_url('/')
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
            return self.render_template("all.html", params=params)
        else:
            return self.redirect_to("main")
class SingleMessageHandler(BaseHandler):
    def get(self, message_id):
        user = users.get_current_user()
        if user:
            prijavljen = True
            message = Message.get_by_id(int(message_id))
            params = {"message": message}
            params["user"] = user
            logout_url = users.create_logout_url('/')
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
            return self.render_template("single_message.html", params=params)
        else:
            return self.redirect_to("main")
class NewMessageHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            prijavljen = True
            logout_url = users.create_logout_url('/')
            m_sender = Message.query(Message.sender == user.email()).fetch()
            params = {"m_sender": m_sender}
            params["user"] = user
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
            return self.render_template("new.html", params=params)
        else:
            return self.redirect_to("main")
class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        user = users.get_current_user()
        if user:
            prijavljen = True
            message = Message.get_by_id(int(message_id))
            params = {"message": message}
            params["user"] = user
            logout_url = users.create_logout_url('/')
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
            return self.render_template("edit_message.html", params=params)
        else:
            return self.redirect_to("main")

    def post(self, message_id):
        user = users.get_current_user()
        input_message = self.request.get("edit_message")
        #input_sender = self.request.get("edit_sender")
        input_sender = user.email()
        input_receiver = self.request.get("edit_receiver")
        message = Message.get_by_id(int(message_id))
        message.message = input_message
        message.sender = input_sender
        message.receiver = input_receiver
        message.put()
        return self.redirect_to("all-messages")
class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                prijavljen = True
                message = Message.get_by_id(int(message_id))
                params = {"message": message}
                params["user"] = user
                logout_url = users.create_logout_url('/')
                params["prijavljen"] = prijavljen
                params["logout_url"] = logout_url
                return self.render_template("delete_message.html", params=params)
            else:
                return self.response.write('You are not an administrator.')

        else:
            return self.redirect_to("main")

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.key.delete()
        return self.redirect_to("all-messages")
class ReceivedMessageHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            prijavljen = True
            m_receiver = Message.query(Message.receiver == user.email()).fetch()
            params = {"m_receiver": m_receiver}
            params["user"] = user
            logout_url = users.create_logout_url('/')
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
            return self.render_template("inbox.html", params=params)
        else:
            return self.redirect_to("main")
class SentMessageHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            prijavljen = True
            m_sender = Message.query(Message.sender == user.email()).fetch()
            params = {"m_sender": m_sender}
            params["user"] = user
            logout_url = users.create_logout_url('/')
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
            return self.render_template("outbox.html", params=params)
        else:
            return self.redirect_to("main")
class MessageHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            prijavljen = True
            logout_url = users.create_logout_url('/')
            params = {"prijavljen": prijavljen, "logout_url": logout_url, "user": user}
            return self.render_template("message.html", params)
        else:
            return self.redirect_to("main")
    def post(self):
        user = users.get_current_user()
        input_message = self.request.get("message")
        input_sender = user.email()
        input_receiver = self.request.get("receiver")
        message = Message(message=input_message, sender=input_sender, receiver=input_receiver)
        message.put()
        return self.write("You have written: " + input_message + " " + input_sender + " " + input_receiver)
class WeatherHandler(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=Zagreb&units=metric&appid=7e4ae2adf3e1ccff3757552de640d8cb"
        result = urlfetch.fetch(url)
        url_data = json.loads(result.content)
        params = {"data": url_data}
        user = users.get_current_user()
        params["user"] = user
        if user:
            prijavljen = True
            logout_url = users.create_logout_url('/')
            params["prijavljen"] = prijavljen
            params["logout_url"] = logout_url
        else:
            prijavljen = False
            login_url = users.create_login_url('/')
            params["prijavljen"] = prijavljen
            params["login_url"] = login_url
        return self.render_template("weather.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/result', MessageHandler),
    webapp2.Route('/all', AllMessagesHandler, name="all-messages"),
    webapp2.Route('/new', NewMessageHandler),
    webapp2.Route('/single_message/<message_id:\\d+>', SingleMessageHandler),
    webapp2.Route('/single_message/<message_id:\\d+>/edit', EditMessageHandler),
    webapp2.Route('/single_message/<message_id:\\d+>/delete', DeleteMessageHandler),
    webapp2.Route('/outbox', SentMessageHandler),
    webapp2.Route('/inbox', ReceivedMessageHandler),
    webapp2.Route('/weather', WeatherHandler),
], debug=True)

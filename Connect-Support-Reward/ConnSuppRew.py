from google.appengine.api import users
from google.appengine.ext import db


import os
import jinja2
import datetime
import webapp2
import cgi

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        test = "Not a member"

        if user:

            test = userAMember(user.user_id())
            if test:
                greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
            else:
                greeting="Null"
                self.redirect("/join")
                #add_user(user.nickname(), "Bob", "Test University", "Helping Others")
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        # Setup template values
        template_values = {
            'greeting': greeting,
            'name': test,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Join(webapp2.RequestHandler):
    def get(self):
        user= users.get_current_user()
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.user_id(), users.create_logout_url('/')))
        template_values={
            'greeting': greeting,
        }

        template = JINJA_ENVIRONMENT.get_template('completeProfile.html')
        self.response.write(template.render(template_values))

class Member(db.Model):
    userID= db.StringProperty(indexed=True)
    fName=db.StringProperty(indexed=False)
    homeSchool=db.StringProperty(indexed=True)
    categories = db.StringProperty(indexed=True)
    joinDate = db.DateProperty(auto_now_add=True)

def userAMember(user_id):
    holder = Member.all()
    holder.filter("userID = ", user_id)
    if not holder.get():
        return False
    else: 
        return True

def add_user(userid, name, school, interest):
    newUser = Member(userID = userid, fName=name, homeSchool=school, categories=interest)
    newUser.joinDate = datetime.datetime.now().date()
    newUser.put()

class Signup(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        name = self.request.get('fname')
        school = self.request.get('location')
        interest = self.request.get_all('interest')
        interest = ', '.join(interest)
        add_user(user.user_id(), name, school, interest)
        self.redirect("/")


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


application = webapp2.WSGIApplication([
    ('/', MainPage),('/join',Join), ('/signup', Signup),
], debug=True)

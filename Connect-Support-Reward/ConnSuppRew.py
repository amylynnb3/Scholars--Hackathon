from google.appengine.api import users
from google.appengine.ext import ndb

import os
import jinja2

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        self.response.out.write('<html><body>%s</body></html>' % greeting)
        # Setup template values
        template_values = {
            'name': 'Julien',
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Member(ndb.Model):
    userID= ndb.StringProperty(indexed=False)
    fName=ndb.StringProperty(indexed=False)
    homeSchool=ndb.StringProperty(indexed=True)
    categories = ndb.StringProperty(indexed=True)
    joinDate = ndb.DateTimeProperty(auto_now_add=True)

def add_user(id, name, school, interest, date):
    newUser = Member(userID = id, fname=name, homeSchool=school, categories=interest)
    newUser.joinDate = datetime.datetime.now().date()
    newUser.put()

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

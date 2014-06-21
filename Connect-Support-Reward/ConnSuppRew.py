from google.appengine.api import users
from google.appengine.ext import ndb

import os
from google.appengine.ext import ndb
import jinja2

import webapp2

INTEREST_LIST_ROOT = 'interest_list_root'

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        # Setup template values
        template_values = {
            'greeting': greeting,
            'name': 'Julien',
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

def interestlist_key():
    """Returns the root node of all interests (interest list)"""
    return ndb.Key('InterestList', INTEREST_LIST_ROOT)

class Interest(ndb.Model):
    """Models an individual interest."""
    interest = ndb.StringProperty()

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


# Ugly code - statically add all interests. Should be done dynamically later on.
interest_names  = { 'Seeking Homework Help',
                    'Professor and Course Suggestions',
                    'Support Groups',
                    'Tutoring Others',
                    'Social Events',
}

for interest_name in interest_names:
    print "Adding %s" % (interest_names)
    # Check if already exists. If this is the case, then skip.
    interests_query = Interest.query(
        Interest.interest==interest_name)
    interests = interests_query.fetch()
    if (len(interests)==0):
        # Create the new interest
        interest = Interest( parent=interestlist_key() )
        interest.interest = interest_name
        interest.put()

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

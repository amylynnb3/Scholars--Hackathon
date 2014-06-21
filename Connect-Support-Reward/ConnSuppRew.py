from google.appengine.api import users
from google.appengine.ext import db


import os
from google.appengine.ext import ndb
import jinja2
import datetime
import webapp2
import cgi

INTEREST_LIST_ROOT = 'interest_list_root'

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        test = "Not a member"

        if user:

            test = userAMember(user.user_id())
            if test:
                greeting = "Null"
                self.redirect("/viewProfile/"+user.user_id())
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

# TODO: MYPROFILE

class ViewProfile(webapp2.RequestHandler):
    def get(self, userID=None):
        
        if userID is None:
            # View my profile instead so fetch myself
            myProfile = True
            user = users.get_current_user()
            userID = user.user_id()
            print "USERID=%s" % (userID)
        else:
            myProfile = False
        
        member = Member.all().filter("userID =", userID).fetch(1)[0]

        # Hack - pull categories as array
        categories_array = member.getCategoriesAsArray();

        template_values = {
            'userid': userID,
            'member': member,
            'categories': categories_array,
        }

        template = JINJA_ENVIRONMENT.get_template('viewProfile.html')
        self.response.write(template.render(template_values))


class Join(webapp2.RequestHandler):
    """Page for users to become members"""
    def get(self):
        user= users.get_current_user()
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        template_values={
            'greeting': greeting,
        }

        template = JINJA_ENVIRONMENT.get_template('completeProfile.html')
        self.response.write(template.render(template_values))

class Member(db.Model):
    """Models a user"""
    userID= db.StringProperty(indexed=True)
    fName=db.StringProperty(indexed=False)
    homeSchool=db.StringProperty(indexed=True)
    categories = db.StringProperty(indexed=True)
    joinDate = db.DateProperty(auto_now_add=True)
    def getCategoriesAsArray(self):
        return self.categories.split(',');

class Signup(webapp2.RequestHandler):
    """ Signup page """
    def post(self):
        user = users.get_current_user()
        name = self.request.get('fname')
        school = self.request.get('location')
        interest = self.request.get('interest', allow_multiple=True)
        interest = ', '.join(interest)
        add_user(user.user_id(), name, school, interest)
        self.redirect("/viewProfile/"+user.user_id())

def getUserName(user_id):
    """ Return members name"""
    holder = Member.all()
    holder.filter("userID = ", user_id)
    p = holder.get()
    return p.fName




def userAMember(user_id):
    """Returns true if user is a member of the site"""
    holder = Member.all()
    holder.filter("userID = ", user_id)
    if not holder.get():
        return False
    else: 
        return True

def interestlist_key():
    """Returns the root node of all interests (interest list)"""
    return ndb.Key('InterestList', INTEREST_LIST_ROOT)

class Interest(ndb.Model):
    """Models an individual interest."""
    interest = ndb.StringProperty()

def add_user(id, name, school, interest, date):
    newUser = Member(userID = id, fname=name, homeSchool=school, categories=interest)

def add_user(userid, name, school, interest):

    if userAMember(userid):
       None
    else:
        newUser = Member(userID = userid, fName=name, homeSchool=school, categories=interest)
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
    ('/myProfile', ViewProfile),
    ('/viewProfile/(\w+)', ViewProfile),
    ('/', MainPage),('/join',Join), ('/signup', Signup),
], debug=True)

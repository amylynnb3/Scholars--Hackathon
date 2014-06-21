from google.appengine.api import users
from google.appengine.ext import db


import os
from google.appengine.ext import ndb
import jinja2
import datetime
import webapp2
import cgi
import logging
import time
import urllib2
import urllib
import json

INTEREST_LIST_ROOT = 'interest_list_root'
API_KEY = 'AIzaSyBSk4BiVJLSiin08v1Tby69sLVDkBAoyho'

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
                #add__or_update_user(user.nickname(), "Bob", "Test University", "Helping Others")
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
        
        member = Member.all().filter("userID =", userID).fetch(1)

        if(len(member) > 0):
        	member = member[0]
        else:
        	member = ""
        interest_array = []
        # Hack - pull categories as array
        if(member != ""):
        	categories_array = member.getCategoriesAsArray();
	        # Retrieve complete interest info for each category
	        for category in categories_array:
	            interests_query = Interest.query( Interest.interestkey==category )
	            i = interests_query.fetch()
	            if(len(i) > 0):
	            	interest_array.append(i[0].interest)
	    	

        refers_num = Refers.getReferalNum(userID)
        profilePic = getProfilePic(userID)
        template_values = {
            'userid': userID,
            'member': member,
            'categories': interest_array,
            'refers_num': refers_num,
            'myProfile': (userID == users.get_current_user().user_id()),
            'myID': users.get_current_user().user_id(),
            'profilePic': profilePic
        }

        template = JINJA_ENVIRONMENT.get_template('viewProfile.html')
        self.response.write(template.render(template_values))


class Join(webapp2.RequestHandler):
    """Page for users to become members"""
    def get(self):
        user= users.get_current_user()
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %

        (user.nickname(), users.create_logout_url('/')))

        # Fetch the list of interests
        interests_query = Interest.query( ancestor=interestlist_key() )
        interests = interests_query.fetch()

        memberfName = ''
        memberhomeSchool = ''

        # Build a triple - intereststate: interestkey, interest, checked(or not)
        intereststate = []
        for interest in interests:
            intereststate.append( {
                'interestkey': interest.interestkey,
                'interest': interest.interest,
                'state': ''
            } );

        # If the user is already a member, then it shall be edited :-)
        if userAMember(user.user_id()):
            # Prefill its values to edit it
            member = Member.all().filter("userID =", user.user_id()).fetch(1)

            if(member != None):
                member = member[0]

                # Prefill stuff
                memberfName = member.fName
                memberhomeSchool = member.homeSchool
                
                membercategories = member.getCategoriesAsArray()
                # Mark all member cats as checked
                for intstate in intereststate:
                    if intstate['interestkey'] in membercategories:
                        intstate['state'] = 'checked'

        template_values={
            # Prefill default values that are not used for new profiles
            'memberfName':memberfName,
            'memberhomeSchool':memberhomeSchool,
            'greeting': greeting,
            'intereststate': intereststate,
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
        categories = self.categories.split(',')
        rcategories = []
        for cat in categories:
            rcategories.append(cat.strip())
        return rcategories

class Signup(webapp2.RequestHandler):
    """ Signup page """
    def post(self):
        user = users.get_current_user()
        name = self.request.get('fname')
        school = self.request.get('location')
        interest = self.request.get('interest', allow_multiple=True)
        interest = ', '.join(interest)
        # Add or update user
        member = add_or_update_user(user.user_id(), name, school, interest)
        # Wait a bit
        time.sleep(2)
        self.redirect("/viewProfile/"+user.user_id())


class Action(webapp2.RequestHandler):
    """Button functionality for each page"""
    def post(self):
        typeofaction = self.request.get('edit')
        self.response.write(typeofaction)
        if typeofaction=="Search Other Users":
            self.redirect("/search")
        elif (typeofaction == "Search"):
            location= self.request.get('location')
            interest = self.request.get('interest', allow_multiple=True)
            interest = ','.join(interest)
            self.redirect("/searchresults?school="+location+'&interest='+interest)

        elif typeofaction=="Edit my Profile":
            self.redirect("/join")
        elif typeofaction=="Thank You!":
            referID = self.request.get('referID')
            userID = self.request.get('userID')
            print "userID is " + userID
            print "referID is " + referID
            Refers.addRefers(userID, referID)
            time.sleep(1)
            self.redirect("/viewProfile/"+userID)

        elif (typeofaction=="Logout"):
            self.redirect(users.create_logout_url('/'))

        elif (typeofaction =="Login"):
            self.redirect(users.create_login_url('/'))
            
        elif (typeofaction == "My Profile"):
            user = users.get_current_user();
            self.redirect("/myProfile")


class Search (webapp2.RequestHandler):
   
    def get(self):
        interests_query = Interest.query(
            ancestor=interestlist_key())
        interests = interests_query.fetch()

        template_values={
            'interests': interests,
            'logout':users.create_logout_url('/')
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

class SearchResults (webapp2.RequestHandler):
    def get(self):
        user= users.get_current_user()
        school = self.request.get('school')
        #self.response.write(school)
        interests = self.request.get('interest')
        interests = interests.split(',')
        memberlist=[]
        holder=Member.all()
        if school != "":
            holder.filter('homeSchool =',school)
            #self.response.write(holder.get().fName)
        flag=True
        for s in holder.run():
            self.response.write(s)
            for p in interests:
                if p not in s.categories:
                   # self.response.write(s.categories)
                    flag = False
                    break
                else:
                    flag = True
            if flag:
                memberlist.append([s.userID,s.fName, Refers.getReferalNum(s.userID), user.user_id()])
        #self.response.write(memberlist)
        template_values = {
            'searchResult':memberlist 
        }
        template= JINJA_ENVIRONMENT.get_template('searchresults.html')
        self.response.write(template.render(template_values))

def getUserName(user_id):
    """ Return members name"""
    holder = Member.all()
    holder.filter("userID = ", user_id)
    p = holder.get()
    return p.fName

def getUserID(name):
    """Return a member's id given a member's name"""
    holder = Member.all()
    holder.filter("fName = ", name)
    p = holder.get()
    return p.userID


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
    interestkey = ndb.StringProperty()
    interest = ndb.StringProperty()

def add_or_update_user(userid, name, school, interest):

    # Update existing member
    if userAMember(userid):
        member = Member.all().filter("userID =", userid).fetch(1)

        if(member != None):
            member = member[0]
            member.fName = name
            member.homeSchool = school
            member.categories = interest
    else:
        # Create new member
        member = Member(userID = userid, fName=name, homeSchool=school, categories=interest)
        member.joinDate = datetime.datetime.now().date()
        refers = Refers(userID = userid, refers = [])
        refers.put()
    
    # Save member
    member.put(deadline=60)

def getProfilePic(id):
    req = "https://www.googleapis.com/plus/v1/people/" + id + "?fields=image&key=" + API_KEY
    default = "https://www.googleapis.com/plus/v1/people/105168348107704411028?fields=image&key=" + API_KEY
    print "trying to get profile pic"
    print req
    url = ""
    try:
            print urllib2.urlopen(req).read()
            result = urllib2.urlopen(default)
            resultJSON = json.loads(result.read())
            print resultJSON
            url = resultJSON['image']['url']
    except urllib2.URLError, exception_variable:
            print exception_variable.reason
            print "id is does not exist and there is no profile picture"
            print "getting default picture"
            result = urllib2.urlopen(default)
            resultJSON = json.loads(result.read())
            print resultJSON
            url = resultJSON['image']['url']
    return url

class Refers(db.Expando):
	userID = db.StringProperty()
	refers = db.StringListProperty()

	@classmethod
	def getRefers(cls,id):
		"""given the user id, this returns the referals a user has"""
		q = cls.all()
		q.filter("userID = ", id)
		for i in q:
			print i.refers
		return q

	@classmethod
	def getReferalNum(cls, id):
		"""given the user id, this returns the number of referals a user has"""
		q = cls.all()
		q.filter("userID = ", id)
		if(q != None and q.get() != None):
			r = q.get()
			return len(r.refers)
		else:
			return 0

	@classmethod
	def addRefers(cls,id, referID):
		"""given the user id and a referID, this adds a referID to the list of refers that belongs to the user"""
		q = cls.all()
		q.filter("userID = ", id)
		print "trying to add refers"
		if(q != None):
			r = q.get()
			referList = r.refers
			print "user id is " + id
			print "user that will refer is " + referID
			print "refer list:"
			print referList
			print referID in referList
		if((referID in referList) == False and id != referID):
			referList.append(referID)
			print "added " + referID + " to the referList for user with id " + id
		else:
			print "user with id " + referID + " has already referred user with id " + id 
		r.refers = referList
		r.put()
		return referList



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Ugly code - statically add all interests. Should be done dynamically later on.
interest_list  = { ('seeking', 'Seeking Homework Help'),
                    ('professor', 'Professor and Course Suggestions'),
                    ('support', 'Support Groups'),
                    ('tutor', 'Tutoring Others'),
                    ('social', 'Social Events'),
}

for (interest_key, interest_name) in interest_list:
    print "Adding %s" % (interest_name)
    # Check if already exists. If this is the case, then skip.
    interests_query = Interest.query(
        Interest.interestkey==interest_key)
    interests = interests_query.fetch()
    if (len(interests)==0):
        # Create the new interest
        interest = Interest( parent=interestlist_key() )
        interest.interestkey = interest_key
        interest.interest = interest_name
        interest.put()

# print "testing adding refers"
# Refers.addRefers("185804764220139124118", "117015317981368465184")
# print "testing getting refers"
# Refers.getRefers("185804764220139124118")
# Refers.getRefers("117015317981368465184")
# print "testing getting refer list amount"
# print Refers.getReferalNum("185804764220139124118")
# print Refers.getReferalNum("117015317981368465184")

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/myProfile', ViewProfile),
    ('/viewProfile/(\w+)', ViewProfile),
    ('/', MainPage),('/join',Join), ('/signup', Signup), ('/action',Action), ('/search', Search), ('/searchresults', SearchResults),
], debug=True)

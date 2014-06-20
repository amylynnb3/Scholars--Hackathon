from google.appengine.api import users

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

        # Setup template values
        template_values = {
            'greeting': greeting,
            'name': 'Julien',
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

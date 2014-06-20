import os
import jinja2
import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        # Setup template values
        template_values = {
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

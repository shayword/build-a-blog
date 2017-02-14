import os
import re
import cgi
import sys
import logging
from urllib2 import Request, urlopen, URLError
from xml.dom import minidom

import webapp2
import jinja2

from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Blog(db.Model):
	title=db.StringProperty(required=True)
	blogtext=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class BlogPage(Handler):
	def render_BlogPage(self, title = "", blogtext = ""):
		blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC ")

		self.render("BlogPage.html", blogs = blogs, title = title, blogtext = blogtext)
	def get(self):
		return self.render_BlogPage()
		  
class NewPostPage(Handler):
	def render_NewPostPage(self, title="", blogtext="", error=""):

		self.render("NewPostPage.html", title = title, blogtext = blogtext, error = error)

	def get(self):
		self.render("NewPostPage.html")

	def post(self):
		title = self.request.get("title")
		blogtext = self.request.get("blogtext")

		if title and blogtext:
			b = Blog(title = title, blogtext = blogtext)
			b.put()

			self.redirect("/")
		else:
			error= "You must enter both a title and blog content!"
			self.render_NewPostPage(title, blogtext, error)

class ViewBlogHandler(webapp2.RequestHandler):
    def get(self, id):
        pass #replace this with some code to handle the request


app = webapp2.WSGIApplication([
    ('/', BlogPage),
	('/newpost', NewPostPage),
	webapp2.Route('/blog/<id:\d+>', ViewBlogHandler)
], debug=True)

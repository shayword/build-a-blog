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

template_base = jinja_env.get_template("base.html")

def get_posts(limit, offset):
    blogs = db.GqlQuery('SELECT * FROM Blog '
                        'ORDER BY created DESC '
                        'LIMIT ' + str(limit) + ' OFFSET ' + str(offset))
    return blogs

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
    def render_front(self, page):
        if page:
            page=int(page)
        else:
            page=1

        limit=5

        if page == 1:
            offset = 0
        else:
            offset=(page-1)*5

        blogs = get_posts(limit,offset)
        offset=(page*5)
        count = blogs.count(offset=offset, limit=limit)
        self.render('BlogPage.html', blogs=blogs, page=page, count=count)

    def get(self):
        page=self.request.get('page')
        self.render_front(page)
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

class ViewPostHandler(webapp2.RequestHandler):

    def get(self, id):
        post = Blog.get_by_id(int (id) )

        if post:
            response = ("<h1><u>" + post.title + "</u></h1>" + "<p>" + "<hr>" + post.blogtext + "</hr>" + "</p>" + "<br><br><br>")
            self.response.write(response)
        else:
            error = "There's no blogpost here, Gandalf Stormcrow."
            self.response.write("<b>" + error + "</b>")
            return

app = webapp2.WSGIApplication([
    ('/', BlogPage),
	('/newpost', NewPostPage),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ^ that's what she said.

# base libraries
import hashlib
import hmac
import random
import re
import os

# apengine specific
import webapp2
import jinja2

# shortcuts
from google.appengine.ext import db
from string import letters


# templating settings
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = False) 

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('los fricos')

class BlogHandler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(**params)
        
    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs)) 

class WikiHandler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(**params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        wat = BlogHandler()
        return wat.render_str('post.html', p = self)

class Page(db.Model):
    title = db.StringProperty()
    content = db.TextProperty()
    date_added = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class User(db.Model):
    name = db.StringProperty(required=True)
    salt = db.StringProperty(required=True)
    passh = db.StringProperty()
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

def wiki_key(name = 'default'):
    return db.Key.from_path('pages', name)

class WikiPage(WikiHandler):
    def get(self,pid):
        page = db.GqlQuery("SELECT * FROM Page WHERE title = :1", pid[1:])
        page = list(page)
        if page:
            self.render('wikifront.html', user=self.request.cookies.get('name'), 
            page=pid, content=page[0].content, prev=self.request.path, edit=True)
        else:
            self.redirect('/_edit' + pid)

class EditWiki(WikiHandler):
    def get(self, pid):
        self.render('editwiki.html', user=self.request.cookies.get('name'), page=pid, 
            prev=self.request.path, view=True)
    def post(self, pid):
        page = list(db.GqlQuery("SELECT * FROM Page WHERE title = :1", pid[1:]))
        if page:
            page = page[0]
            page.content = self.request.POST.get('text')
            page.put()
        else:
            page = Page(title=pid[1:], content=self.request.POST.get('text'))
            page.put()
        self.redirect(pid)
        
class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts = posts)
        
class BlogPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key()) 
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render('permalink.html', post=post)

class NewPost(BlogHandler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' %  str(p.key().id()))
        else:
            error = 'y u no subjct ???'
            self.render('newpost.html', subject=subject, content=content, error=error)
def make_salt():
    return ''.join(i for i in random.sample(letters, 5))

class Register(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('register.html').render())

    def post(self):
        username = self.request.POST.get('username')
        user_re = r"^[a-zA-Z]{3,16}$"
        user_check = re.compile(user_re)
        user_error = u"yo naem fayulz. try %s" % user_re if not user_check.match(username) else ''

        password = self.request.POST.get('password')
        pass_re = r".{4,20}"
        pass_check = re.compile(pass_re)
        pass_error = u"sily paswordz. do lyk dis %s" % pass_re if not pass_check.match(password) else ''

        verify = self.request.POST.get('verify')
        ver_error = u"Y U NO MATHC???" if verify != password else ''

        email = self.request.POST.get('email')
        ema_re = r"^[\w%+-]+@[a-zA-Z0-9.-]+\.[A-zA-Z]{2,6}$"
        ema_check = re.compile(ema_re)
        ema_error = ema_re if not ema_check.match(email) and email else ''

        test_user = User.gql("WHERE name = :name", name=username).get()
        if test_user:
            user_error = u'IZ TAKEN ALREADY.'
                   
        if user_error or pass_error or ver_error or ema_error:
            self.response.out.write(jinja_env.get_template('register.html').render(user_error=user_error,
                                                                                   username=username,
                                                                                   pass_error=pass_error,
                                                                                   ver_error=ver_error,
                                                                                   email=email,
                                                                                   ema_error=ema_error
                                                                                   ))       
        else:
            # so help me God I will refactor this handler some day.
            salt = make_salt()
            passh = hmac.new(salt, password, hashlib.sha256).hexdigest()
            user = User(name=username, salt=salt, passh=passh, email=email)
            user.put()
            self.response.headers.add_header(str('Set-Cookie'), str('name=%s; Path=/' % username))
            self.response.headers.add_header(str('Set-Cookie'), str('pass=%s; Path=/' % passh))
            self.redirect('/regsux')

class Login(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('login.html').render())
    
    def post(self):
        username = self.request.POST.get('username')
        # first check if name is correct
        user_re = r"^[a-zA-Z]{3,16}$"
        user_check = re.compile(user_re)
        user_error = u"yo naem fayulz. try %s" % user_re if not user_check.match(username) else ''
        pass_error = ''
        var = ''
        # then check if he exists in our db
        if not user_error:
            test_user = User.gql("WHERE name = :name", name=username).get()
            if test_user:
                # check password match nao
                password = self.request.POST.get('password')
                ver = hmac.new(str(test_user.salt), str(password), hashlib.sha256).hexdigest()
                if ver != test_user.passh:
                    pass_error = u'yo pass no match.'
            else:
                user_error = u'u no belongz hier sir. move along.'
         
        # redirect for success
        if user_error or pass_error:
            self.response.out.write(jinja_env.get_template('login.html').render(user_error=user_error,
                                                                                   username=username,
                                                                                   pass_error=pass_error,
                                                                                  ))
        else:
            self.response.headers.add_header(str('Set-Cookie'), str('name=%s; Path=/' % username))
            self.response.headers.add_header(str('Set-Cookie'), str('pass=%s; Path=/' % ver))
            self.redirect('/logged')

class Logged(webapp2.RequestHandler):
    def get(self):
        name = self.request.cookies.get('name')
        self.response.out.write('welcum back, <b>%s</b>!' % name) 

class Logout(webapp2.RequestHandler):
    def get(self):
        self.response.headers.add_header(str('Set-Cookie'), str('name=; Path=/'))
        self.response.headers.add_header(str('Set-Cookie'), str('pass=; Path=/'))
        self.redirect(self.request.GET.get('prev'))
    
class Welcum(webapp2.RequestHandler):
    def get(self):
        name = self.request.cookies.get('name')
        if name:
            self.response.out.write('welcum, <b>%s</b>! u haev suksexful rejistrd!' % name) 
        else:
            self.redirect('/signup')

class Portfolio(WikiHandler):
    """Renders my portfolio."""
    def get(self):
        self.render("portfolio.html")

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

app = webapp2.WSGIApplication([('/', MainHandler),
                              # ('/blog/?', BlogFront),
                              # ('/blog/([0-9]+)', BlogPost),
                              # ('/blog/newpost', NewPost),
                               ('/signup/?', Register),
                               ('/login/?', Login),
                               ('/logged/?', Logged),
                               ('/logout/?', Logout),
                               ('/regsux/?', Welcum),
                               ('/about/?', Portfolio),
                               ('/_edit' + PAGE_RE, EditWiki),
                               (PAGE_RE, WikiPage),
                              ],
                              debug=True)

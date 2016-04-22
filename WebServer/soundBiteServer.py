import os, os.path
import random
import string
import cherrypy
import sys
from cherrypy.lib import sessions
from riak import RiakClient, RiakNode
from jinja2 import Environment, FileSystemLoader

# declare global variables
env = Environment(loader=FileSystemLoader('staticFiles/templates'))
riakClient = RiakClient(protocol='http', host='datatwo.csse.rose-hulman.edu', http_port=8098)
userbucketName = "usernames"

class ServeSite(object):
	@cherrypy.expose
	def index(self):
		tmpl = env.get_template('index.html')
		return tmpl.render()

	@cherrypy.expose
	def createUser(self, name, username, password):
		userBucket = riakClient.bucket(userbucketName)
		userValues = {"name": name, "password": password, "salt": username + "salt"}
		userKey = userBucket.new(username, data=userValues)
		userKey.store()
		tmpl = env.get_template('index.html')
		return tmpl.render()

if __name__ == '__main__':
	conf = {
		'global': {
		'server.max_request_body_size': 0
		},
		'/': {
			'tools.sessions.on' : True,
			'tools.staticdir.root' : os.path.abspath(os.getcwd())
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './staticFiles'
		}
	}

cherrypy.server.socket_host = '127.0.0.1'
cherrypy.quickstart(ServeSite(), '/',conf)



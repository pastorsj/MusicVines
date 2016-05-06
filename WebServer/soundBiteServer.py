import os, os.path
import hashlib
import Neo4jTesting
import random
import string
import cherrypy
import sys
import gridfs
from cherrypy.lib import sessions
import riak
from riak import RiakClient, RiakNode
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader

# declare global variables
env = Environment(loader=FileSystemLoader('staticFiles/templates'))
riakClient = RiakClient(protocol='http', host='datatwo.csse.rose-hulman.edu', http_port=8098)
userbucketName = "usernames"
mongoClient = MongoClient('dataone.csse.rose-hulman.edu', 27017)
mongoDB = mongoClient.test

class ServeSite(object):
	@cherrypy.expose
	def index(self, message=''):
		if(cherrypy.session.get('loggedIn', 'None') == True):
			raise cherrypy.HTTPRedirect("/uploadPage")
		else:
			tmpl = env.get_template('home.html')
			return tmpl.render()%message

	@cherrypy.expose
	def register(self,errorMessage=""):
		if(cherrypy.session.get('loggedIn', 'None') == True):
			raise cherrypy.HTTPRedirect("/uploadPage")
		else:
			tmpl = env.get_template('register.html')
			return tmpl.render()%errorMessage

	@cherrypy.expose
	def createUser(self, name, username, password):
		userBucket = riakClient.bucket(userbucketName)
		if(username in userBucket.get_keys()):
			raise cherrypy.HTTPRedirect("/register?errorMessage='Username already Taken'")
		else:
			salt = username+"salt"
			m = hashlib.sha1(password.encode()+salt.encode())
			password = m.hexdigest()
			userValues = {"name": name, "password": password, "salt": username + "salt"}
			userKey = userBucket.new(username, data=userValues)
			userKey.store()
			Neo4jTesting.neoAddUser(username)
			cherrypy.session['loggedIn'] = True
			cherrypy.session['username'] = username
			raise cherrypy.HTTPRedirect("/uploadPage")

	# for testing
	@cherrypy.expose
	def displayUsers(self):
		userBucket = riakClient.bucket(userbucketName)
		users = ""
		for user in userBucket.get_keys():
			users = users + "<p>" + user + "</p>"
		return users

	@cherrypy.expose
	def login(self, username, password):
		userBucket = riakClient.bucket(userbucketName)
		if(username in userBucket.get_keys()):
			userData = userBucket.get(username).data
			associatedPassword = userData['password']
			salt = userData['salt']
			m = hashlib.sha1(password.encode()+salt.encode())
			salted = str(password+salt)
			hashedPassword = m.hexdigest()
			if(associatedPassword == hashedPassword):
				cherrypy.session['loggedIn'] = True
				cherrypy.session['username'] = username
				raise cherrypy.HTTPRedirect("/uploadPage")
			else:
				cherrypy.session['loggedIn'] = False
				raise cherrypy.HTTPRedirect("/index?message='invalid password'")
		else:
			raise cherrypy.HTTPRedirect("/index?message='user does not exist'")
	
	@cherrypy.expose
	def signOut(self):
		cherrypy.session['loggedIn'] = False
		username = cherrypy.session.get('username', 'None')
		fs = gridfs.GridFS(mongoDB)
		for soundFile in fs.find({"username": username}):
			filename = "sounds/" + soundFile.filename
			os.remove(filename)

		cherrypy.session['username'] = None
		raise cherrypy.HTTPRedirect("/index")
	
	@cherrypy.expose
	def uploadPage(self, uploadMessage=''):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			tmpl = env.get_template('uploadPage.html')
			return tmpl.render()%uploadMessage
		else:
			raise cherrypy.HTTPRedirect("/index")

	@cherrypy.expose
	def uploadMP3(self, uploadedFile, sName, tags):
		if(uploadedFile.file is None):
			return """Must provide a file"""
		elif(cherrypy.session.get('loggedIn', 'None') == False):
			raise cherrypy.HTTPRedirect("/uploadPage?uploadMessage='Must be logged in!'")
		else:			
			fileData = uploadedFile.file.read()
			fs = gridfs.GridFS(mongoDB)
			uName = cherrypy.session.get('username', 'None')
			tags = str(tags).split(",")
			tags = map(str.strip, tags)
			filePutID = fs.put(fileData, filename=sName, username=uName)
			Neo4jTesting.neoAddSong(filePutID, sName)
			Neo4jTesting.neoAddUserSong(uName, filePutID)
			for tag in tags:
				Neo4jTesting.neoAddTag(filePutID, tag)			
			raise cherrypy.HTTPRedirect("/uploadPage?uploadMessage='Upload successful!'")
	
	# for testsng
	@cherrypy.expose
	def uploadedSounds(self):
		if(cherrypy.session.get('loggedIn','None')==True):
			fs = gridfs.GridFS(mongoDB)
			username = cherrypy.session.get('username', 'None')
			fileNames = ""
			for soundFile in fs.find({"username": username}):
				fileNames = fileNames + "<p>" + soundFile.filename + "</p>"

			return fileNames
		else:
			raise cherrypy.HTTPRedirect("/index")
			
	@cherrypy.expose
	def allFiles(self):
		fs = gridfs.GridFS(mongoDB)
		userBucket = riakClient.bucket(userbucketName)
		allSounds = ""
		for user in userBucket.get_keys():
			for soundFile in fs.find({"username": user}):
				allSounds = allSounds + "<p>" + soundFile.filename + "</p>"

		return allSounds

	@cherrypy.expose
	def playSounds(self):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			fs = gridfs.GridFS(mongoDB)
			username = cherrypy.session.get('username', 'None')
			soundHtml = """<a href="/uploadPage">Upload Page</a>"""
			for soundFile in fs.find({"username": username}):
				soundFilename = soundFile.filename
				filename = "sounds/" + soundFilename
				fileForSound = open(filename, 'wb')
				fileForSound.write(soundFile.read())
				fileForSound.close()
				soundHtml = soundHtml + """<div>%s<p><audio controls>
								<source src="%s" type="audio/mpeg">
								Browser does not support this feature
							</audio></p></div>"""%(soundFilename,filename)
			return soundHtml+"</a>"
		else:
			raise cherrypy.HTTPRedirect("/index")

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
		},
		'/sounds': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './sounds'
		}
	}


cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 80
cherrypy.quickstart(ServeSite(), '/',conf)



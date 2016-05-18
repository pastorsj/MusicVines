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
from bson import ObjectId
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
			filePutID = fs.put(fileData, filename=sName)
			print(type(filePutID))
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
	def playSounds(self, user=''):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			fs = gridfs.GridFS(mongoDB)
			username = ""
			if(user==''):
				username = cherrypy.session.get('username', 'None')
			else:
				username = user

			songIDs = Neo4jTesting.neoGetUserSongs(username)
			soundHtml = ""
			for song in songIDs:
				soundFile = fs.get(ObjectId(song))
				soundFilename = soundFile.filename
				filename = "sounds/" + soundFilename
				fileForSound = open(filename, 'wb')
				fileForSound.write(soundFile.read())
				fileForSound.close()
				soundHtml = soundHtml + """<div>%s<p><audio controls>
								<source src="%s" type="audio/mpeg">
								Browser does not support this feature
							</audio><form method="post" action="likeSong"><input type="submit" value="Like"><input type="hidden" name="songID" value="%s"><input type="hidden" name="user" value="%s"></form>"""%(soundFilename,filename,song,username)
				if(user==''):
					soundHtml = soundHtml + """<form method="post" action="deleteSong"><input type="submit" value="Delete Song"><input type="hidden" name="songID" value="%s"></form>"""%song
			soundHtml = soundHtml+"</p></div></a>"
			tmpl = env.get_template('playSounds.html')
			return tmpl.render()%soundHtml
		else:
			raise cherrypy.HTTPRedirect("/index")

	@cherrypy.expose
	def likeSong(self, songID, user, recommended='false'):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			username = cherrypy.session.get('username', 'None')
			Neo4jTesting.neoAddLike(username, songID)
			if(recommended=='false'):
				if(username==user):
					raise cherrypy.HTTPRedirect("/playSounds")
				else:
					raise cherrypy.HTTPRedirect("/playSounds?user='%s'"%user)
			else:
				raise cherrypy.HTTPRedirect('/playRecommended')
		else:
			raise cherrypy.HTTPRedirect("/index")

	@cherrypy.expose
	def friendPage(self):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			friendString = ""
			wannaBeString = ""
			username = cherrypy.session.get('username','None')
			friendList = Neo4jTesting.neoGetFriends(username)
			for friend in friendList:
				friendString = friendString + """<p><a href="playSounds?user=%s">%s</a></p>"""%(friend,friend)
			requestList = Neo4jTesting.neoGetFriendRequests(username)
			for friend in requestList:
				wannaBeString = wannaBeString + """<form method="post" action="addFriend">%s <input type="submit" value="Accept Friend Request"><input type="hidden" value="%s" name="friendToAdd"></form>"""%(friend, friend)
			tmpl = env.get_template('addFriend.html')
			return tmpl.render()%(friendString,wannaBeString)
		else:
			raise cherrypy.HTTPRedirect("/index")

	@cherrypy.expose
	def addFriend(self, friendToAdd):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			username = cherrypy.session.get('username','None')
			Neo4jTesting.neoAddFriend(username, friendToAdd)
			raise cherrypy.HTTPRedirect('/friendPage')
		else:
			raise cherrypy.HTTPRedirect('/index')

	@cherrypy.expose
	def searchByTag(self,songs=''):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			tmpl = env.get_template('searchByTag.html')
			return tmpl.render()%songs
		else:
			raise cherrypy.HTTPRedirect('/index')

	@cherrypy.expose
	def getByTag(self,tagName):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			fs = gridfs.GridFS(mongoDB)
			soundHtml = ""
			songIDs = Neo4jTesting.neoFindByTag(tagName)
			for song in songIDs:
				soundFile = fs.get(ObjectId(song))
				soundFilename = soundFile.filename
				filename = "sounds/" + soundFilename
				fileForSound = open(filename, 'wb')
				fileForSound.write(soundFile.read())
				fileForSound.close()
				soundHtml = soundHtml + """<div>%s<p><audio controls>
                                                                <source src="%s" type="audio/mpeg">
                                                                Browser does not support this feature
                                                        </audio></p></div>"""%(soundFilename,filename)
			tmpl = env.get_template('searchByTag.html')
			return tmpl.render()%soundHtml
		else:
			raise cherrypy.HTTPRedirect('/index')

	@cherrypy.expose
	def deleteSong(self, songID):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			fs = gridfs.GridFS(mongoDB)
			fs.delete(ObjectId(songID))
			Neo4jTesting.neoDeleteSong(songID)
			raise cherrypy.HTTPRedirect('/playSounds')
		else:
			raise cherrypy.HTTPRedirect('/index')

	@cherrypy.expose
	def playRecommended(self):
		if(cherrypy.session.get('loggedIn', 'None')==True):
			username = cherrypy.session.get('username','None')
			fs = gridfs.GridFS(mongoDB)
			byLikeSongIDs = Neo4jTesting.neoGetSimilarByLikes(username)
			byTagsSongIDs = Neo4jTesting.neoGetUserSongs(username)
			likeSoundHtml = ""
			for song in byLikeSongIDs:
				soundFile = fs.get(ObjectId(song))
				soundFilename = soundFile.filename
				filename = "sounds/" + soundFilename
				fileForSound = open(filename, 'wb')
				fileForSound.write(soundFile.read())
				fileForSound.close()
				likeSoundHtml = likeSoundHtml + """<div>%s<p><audio controls>
                                                                <source src="%s" type="audio/mpeg">
                                                                Browser does not support this feature
                                                        </audio><form method="post" action="likeSong"><input type="submit" value="Like"><input type="hidden" name="songID" value="%s"><input type="hidden" name="user" value="%s"><input type="hidden" name="recommended" value='true'></form>"""%(soundFilename,filename,song,username)
			
			tagSoundHtml = ""
			songs = []
			for song in byTagsSongIDs:
				songs = songs + Neo4jTesting.neoGetSimilar(song)
			for song in songs:
				soundFile = fs.get(ObjectId(song))
				soundFilename = soundFile.filename
				filename = "sounds/" + soundFilename
				fileForSound = open(filename, 'wb')
				fileForSound.write(soundFile.read())
				fileForSound.close()
				tagSoundHtml = tagSoundHtml + """<div>%s<p><audio controls>
								<source src="%s" type="audio/mpeg">
								Browser does not support this feature
								</audio><form method="post" action="likeSong"><input type="submit" value="Like"><input type="hidden" name="songID" value="%s"><input type="hidden" name="user" value="%s"><input type="hidden" name="recommended" value='true'></form>"""%(soundFilename,filename,song,username)
			tmpl = env.get_template('recommended.html')
			return tmpl.render()%(likeSoundHtml, tagSoundHtml)
		else:
			raise cherrypy.HTTPRedirect('/index')

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



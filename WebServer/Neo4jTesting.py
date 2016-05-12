#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from neo4j.v1 import GraphDatabase, basic_auth

os.environ["neo4jpass"] = "Cee7mee9i"

graph_db = GraphDatabase.driver("bolt://datathree.csse.rose-hulman.edu", auth=basic_auth("neo4j", os.environ["neo4jpass"]))

def escapeSpecialCharacters ( text ):
    text = text.replace("'", "\\" + "'" )
    text = text.replace('"', "\\" + '"' )
    #text = text.replace("'", "\\" + "'" )
    return text

def neoAddSong(songID, title):
    print(str(songID) + " " + title)
    session = graph_db.session()
    session.run("CREATE (node:Song {ID : " + "'%s'"% str(songID) + ", Title : \'" +escapeSpecialCharacters(title)+ "\'})")
    session.close()
    return

def neoAddTag(songID, tag):
    session = graph_db.session()
    session.run("MATCH (a:Song) WHERE a.ID = '%s'"%str(songID) + " " +
                "MERGE (b:Tag {Name : \'" + escapeSpecialCharacters(tag.lower()) + "\'})"+
                "CREATE UNIQUE (a)-[:TAGGED]->(b);")
    session.close()
    return

def neoAddUser(userName):
    session = graph_db.session()
    session.run("CREATE (node:User {Username: \'" + escapeSpecialCharacters(userName) +"\'})")
    session.close()
    return

def neoAddFriend(userName1, userName2):
    session = graph_db.session()
    session.run("MATCH (a:User),(b:User) "+
		"WHERE a.Username = \'" + escapeSpecialCharacters(userName1) + "\' AND b.Username = \'" + escapeSpecialCharacters(userName2) + "\' "+
		"CREATE (a)-[:FRIENDS]->(b);")
    session.close()    

def neoAddUserSong(userName, songID):
    session = graph_db.session()
    session.run("MATCH (a:User),(b:Song) " +
		"WHERE a.Username = \'" + escapeSpecialCharacters(userName) + "\' AND b.ID = '%s' "%str(songID)+
		"CREATE (a)-[:HASSONG]->(b);")
    session.close()
    return

def neoGetUserSongs(userName):
    session = graph_db.session()
    result = session.run("""MATCH (a:User {Username:"%s"}), (b:Song) """%escapeSpecialCharacters(userName) +
		"""WHERE (a)-[:HASSONG]->(b)"""
		"""RETURN b.ID AS id""")
    return [x['id'] for x in result]

def neoGetFriends(userName):
    session = graph_db.session()
    result = session.run("""MATCH (a:User {Username:"%s"}),(b:User)"""%escapeSpecialCharacters(userName) +
			 """WHERE (a)-[:FRIENDS]->(b) AND (b)-[:FRIENDS]->(a)""" +
			 """RETURN b.Username AS username""")
    session.close()
    return [x['username'] for x in result]

def neoDeleteTag(songID, tag):
    session = graph_db.session()
    session.run("MATCH (a:Song)-[f:TAGGED]->(t:Tag)" +
                "WHERE a.ID = " + str(songID) + " " +
                "and t.Name = \'" + escapeSpecialCharacters(tag.lower()) + "\' " +
                "Delete f")
    session.close()
    return

# def neoReturnID(songTitle, uploader):
#     session = graph_db.session()
#     return session.run("MATCH (a:Song) where a.Title = \'" + songTitle + "\' "
#                        "and a.Uploader = \'" + uploader + "\' " +
#                        "return a.ID")
def neoGetFriendsSongs(userName):
    session = graph_db.session()
    #                                              lol you put "HASHSONG" here - JOEL
    results = session.run("MATCH (a:User)-[:FRIEND]-(b:User)->[:HASSONG]-(c:Song) "+
			"WHERE a.Username = \'" + escapeSpecialCharacters(userName) + "\' return c")
    for record in results:
    	print(record["name"])
    results.close()
    session.close()
    return

def neoGetSimilar(songID):
    session = graph_db.session()
    results = session.run("MATCH (a:Song)-[:TAGGED]->(t:Tag)<-[:TAGGED]-(b:Song) " +
			" WHERE a.ID = '%s'"%escapeSpecialCharacters(str(songID)) +" return b")
    for record in results:
        print(record["name"])
    results.close()
    session.close()
    return

def neoFindByTag(tagName):
    session = graph_db.session()
    result = session.run("MATCH (a:Tag)<-[:TAGGED]-(b:Song) " +
			 "WHERE a.Name = \'" + escapeSpecialCharacters(tagName.lower()) + "\' return b.ID AS id")
    session.close()
    return [x['id'] for x in result]

def neoDeleteSong(songID):
    session = graph_db.session()
    result = session.run("MATCH (a:Song) " +
			"WHERE a.ID = '%s' "%str(songID) +
			"DETACH DELETE a")

def neoGetFriendRequests(username):
    session = graph_db.session()
    result = session.run("""MATCH (a:User {Username:"%s"}),(b:User) WHERE (a)<-[:FRIENDS]-(b) AND NOT (a)-[:FRIENDS]->(b)"""%escapeSpecialCharacters(username) +
			 """RETURN b.Username AS username""")
    session.close()
    return [x['username'] for x in result]

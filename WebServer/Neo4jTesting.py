#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from neo4j.v1 import GraphDatabase, basic_auth
os.environ["neo4jpass"] = "Cee7mee9i"

graph_db = GraphDatabase.driver("bolt://datathree.csse.rose-hulman.edu", auth=basic_auth("neo4j", os.environ["neo4jpass"]))

def neoAddSong(songID, title):
    print(str(songID) + " " + title)
    session = graph_db.session()
    session.run("CREATE (node:Song {ID : " + "'%s'"% str(songID) + ", Title : \'" +title+ "\'})")
    session.close()
    return

def neoAddTag(songID, tag):
    session = graph_db.session()
    session.run("MATCH (a:Song) WHERE a.ID = '%s'"%str(songID) + " " +
                "MERGE (b:Tag {Name : \'" + tag.lower() + " " + "\'})"+
                "CREATE UNIQUE (a)-[:TAGGED]->(b);")
    session.close()
    return

def neoAddUser(userName):
    session = graph_db.session()
    session.run("CREATE (node:User {Username: \'" + userName +"\'})")
    session.close()
    return

def neoAddFriends(userName1, userName2):
    session = graph_db.session()
    session.run("MATCH (a:User),(b:User) "+
		"WHERE a.Username = \'" + userName1 + "\' AND b.Username = \'" + userName2 + "\' "+
		"CREATE (a)-[:FRIEND]-(b);")

def neoAddUserSong(userName, songID):
    session = graph_db.session()
    session.run("MATCH (a:User),(b:Song) " +
		"WHERE a.Username = \'" + userName + "\' AND b.ID = '%s' "%str(songID)+
		"CREATE (a)-[:HASSONG]->(b);")
    session.close()
    return

def neoDeleteTag(songID, tag):
    session = graph_db.session()
    session.run("MATCH (a:Song)-[f:TAGGED]->(t:Tag)" +
                "WHERE a.ID = " + str(songID) + " " +
                "and t.Name = \'" + tag + "\' " +
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
    results = session.run("MATCH (a:User)-[:FRIEND]-(b:User)->[:HASHSONG]-(c:Song) "+
			"WHERE a.Username = \'" + userName + "\' return c")
    for record in results:
	print(record["name"])
    results.close()
    session.close()
    return

def neoGetSimilar(songID):
    session = graph_db.session()
    results = session.run("MATCH (a:Song)-[:TAGGED]->(t:Tag)<-[:TAGGED]-(b:Song) " +
			" WHERE a.ID = '%s'"%str(songID) +" return b")
    for record in results:
        print(record["name"])
    results.close()
    session.close()
    return

def neoFindByTag(tagName):
    session = graph_db.session()
    result = session.run("MATCH (a:Tag)<-[:TAGGED]-(b:Song) " +
			 "WHERE a.Name = \'" + tagName "\' return b")
    for record in results:
	print(record["name"])
    result.close()
    session.close()
    return

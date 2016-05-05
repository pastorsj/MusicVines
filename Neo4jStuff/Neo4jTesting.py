#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from neo4j.v1 import GraphDatabase, basic_auth

graph_db = GraphDatabase.driver("bolt://datathree.csse.rose-hulman.edu", auth=basic_auth("neo4j", os.environ["neo4jpass"]))

def neoAddSong(songID, title, uploader, desc):
    session = graph_db.session()
    session.run("CREATE (node:Song {ID : " + str(songID) + ", Title : \'" +title+ "\', Uploader: \'"+uploader+"\', Description : \'"+desc+"\'})")
    return

def neoAddTag(songID, tag):
    session = graph_db.session()
    session.run("MATCH (a:Song) WHERE a.ID = " + str(songID) + " " +
                "MERGE (b:Tag {Name : \'" + tag.lower() + " " + "\'})"+
                "CREATE UNIQUE (a)-[:TAGGED]->(b);")
    return

def neoDeleteTag(songID, tag):
    session = graph_db.session()
    session.run("MATCH (a:Song)-[f:TAGGED]->(t:Tag)" +
                "WHERE a.ID = " + str(songID) + " " +
                "and t.Name = \'" + tag + "\' " +
                "Delete f")
    return

def neoReturnID(songTitle, uploader):
    session = graph_db.session()
    return session.run("MATCH (a:Song) where a.Title = \'" + songTitle + "\' "
                       "and a.Uploader = \'" + uploader + "\' " +
                       "return a.ID")

def neoGetSimilar(songID):
    session = graph_db.session()
    results = session.run("MATCH (a:Song)-[:TAGGED]->(t:Tag)<-[:TAGGED]-(b:Song) WHERE a.ID = "+ str(songID) +" return b")
    for record in results:
        print(record["name"])

    return

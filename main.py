#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import json
from gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all()

con = sqlite3.connect("feedback.db")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS exempel (
  elev TEXT NULL,
  uppgift TEXT NULL,
  typ TEXT NULL,
  beskrivning TEXT NULL,
  PRIMARY KEY (elev, uppgift, typ)
);""")

cur.execute("""CREATE TABLE IF NOT EXISTS svar (
  exempelid INTEGER NULL,
  elev TEXT NULL,
  svar TEXT NULL,
  feedback TEXT NULL,
  PRIMARY KEY (exempelid, elev)
);""")

con.commit()

def application(env, start_response):
    jsondata = {}
    if env['REQUEST_METHOD'] == "POST":
        length= int(env.get('CONTENT_LENGTH', '0'))
        if length!=0 and ("application/json" in env.get('CONTENT_TYPE', '')):
          jsondata = json.loads(env['wsgi.input'].read(length))
        else:
          start_response('400 Bad Request', [('Access-Control-Allow-Origin', '*'), ('Content-Type', 'application/json')])
          return """{"error":"json required"}"""

    if env['PATH_INFO'] == '/exemepel':
      if env['REQUEST_METHOD'] == "POST":
        values = (
          jsondata["elev"],
          jsondata["uppgift"],
          jsondata["typ"],
          jsondata["beskrivning"],
          jsondata["beskrivning"]
        )
        cur.execute("""
          INSERT INTO exempel(elev, uppgift, typ, beskrivning)
            VALUES(?,?,?,?)
          ON CONFLICT(elev, uppgift, typ) 
            DO UPDATE SET beskrivning=?;
          """, values);
        con.commit()

        values = (
          jsondata["elev"],
          jsondata["uppgift"],
          jsondata["typ"]
        )
        res  = cur.execute("""
          SELECT rowid FROM exempel 
            WHERE elev = ? AND uppgift = ? AND typ = ?;""",
          values)
        id = res.fetchall()[0][0]
        cur.execute("""
          DELETE FROM svar WHERE exempelid = ?;""", (id,));
        con.commit()

        start_response('200 OK', [('Access-Control-Allow-Origin', '*'),('Content-Type', 'application/json')])
        return [bytes(json.dumps({"id":id}), 'utf-8')]
      elif env['REQUEST_METHOD'] == "GET":
        res  = cur.execute("""
          SELECT rowid, elev, uppgift, typ, beskrivning FROM exempel;"""
          )
        def tillDict(rad):
          return {
          "id":rad[0],
          "elev":rad[1],
          "uppgift":rad[2],
          "typ":rad[3],
          "beskrivning":rad[4]
          }
        allaexempel = list(map(tillDict,res.fetchall()))
        start_response('200 OK', [('Access-Control-Allow-Origin', '*'),('Content-Type', 'application/json')])
        return [bytes(json.dumps({"exempel":allaexempel}), 'utf-8')]
      elif env['REQUEST_METHOD'] == "OPTIONS":
        start_response('200 OK', [
          ('Access-Control-Allow-Origin', '*'),
          ('Access-Control-Allow-Credentials', 'true'),
          ("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT"),
          ("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, authorization, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"),
          ('Content-Type', 'text/html')]
        )
      return [b""]

    elif env['PATH_INFO'] == '/svar':
      if env['REQUEST_METHOD'] == "POST":
        values = (
          jsondata["id"],
          jsondata["elev"],
          jsondata["svar"],
          jsondata["feedback"],
          jsondata["svar"],
          jsondata["feedback"]
        )
        cur.execute("""
          INSERT INTO svar(exempelid, elev, svar, feedback)
            VALUES(?,?,?,?)
          ON CONFLICT(exempelid, elev) 
            DO UPDATE SET svar = ?, feedback = ?;
          """, values);
        con.commit()
        values = (
          jsondata["id"],
          jsondata["elev"],
        )
        res  = cur.execute("""
          SELECT rowid FROM svar 
            WHERE exempelid = ? AND elev = ?;""",
          values)
        id = res.fetchall()[0][0]

        start_response('200 OK', [('Access-Control-Allow-Origin', '*'),('Content-Type', 'application/json')])
        return [bytes(json.dumps({"id":id}), 'utf-8')]
      if env['REQUEST_METHOD'] == "GET":
        res  = cur.execute("""
          SELECT rowid, exempelid, elev, svar, feedback FROM svar;"""
          )
        def tillDict(rad):
          return {
          "id":rad[0],
          "elev":rad[1],
          "svar":rad[2],
          "feedback":rad[3]
          }
        allaexempel = list(map(tillDict,res.fetchall()))
        start_response('200 OK', [('Access-Control-Allow-Origin', '*'),('Content-Type', 'application/json')])
        return [bytes(json.dumps({"exempel":allaexempel}), 'utf-8')]
      start_response('200 OK', [('Access-Control-Allow-Origin', '*'),("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, authorization, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"),('Content-Type', 'text/html')])
      return [b"POST/GET supported"]


    else:
      start_response('404 Not Found', [('Access-Control-Allow-Origin', '*'),('Content-Type', 'text/html')])
      return [b'<h1>Not Found</h1>']

print('Serving on 6588...')
WSGIServer(('127.0.0.1', 6588), application).serve_forever()
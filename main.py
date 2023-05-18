#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import bottle
from gevent.pywsgi import WSGIServer
con = sqlite3.connect("feedback.db")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS exempel (
  elev TEXT NULL,
  uppgift TEXT NULL,
  typ TEXT NULL,
  beskrivning TEXT NULL
);""")

cur.execute("""CREATE TABLE IF NOT EXISTS svar (
  exempelid
  elev TEXT NULL,
  svar TEXT NULL
);""")

con.commit()

def application(env, start_response):
    if env['PATH_INFO'] == '/examples':
      """/examples
      POST = add / update
      updatera = radera alla svar"""
      """
      res = cur.execute("SELECT score FROM ")
      res.fetchall()
      """

    elif env['PATH_INFO'] == '/svar':
      """/svar
      POST = add
      GET = alla från uppgift"""
      """
      res = cur.execute("SELECT score FROM ")
      res.fetchall()
      """
      start_response('200 OK', [('Content-Type', 'text/html')])
      return [b"<b>hello world</b>"]

    else:
      start_response('404 Not Found', [('Content-Type', 'text/html')])
      return [b'<h1>Not Found</h1>']

print('Serving on 6588...')
WSGIServer(('127.0.0.1', 6588), application).serve_forever()
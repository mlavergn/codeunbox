#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# __author__ = "Marc Lavergne"
# __copyright__ = "Copyright 2013, Marc Lavergne"
# __license__ = "Modified BSD (http://directory.fsf.org/wiki/License:BSD_3Clause)"

import sys
import os
import sqlite3

def LogConsole(arg):
  print("%s\n" % arg)

#===============================================================================

import base64
import xml.dom.minidom

class Base:

  #-----------------------------------------------------------------------------

  def decode(self, data):
    try:
      return base64.decodestring(data)
    except:
      print sys.exc_info()[0]
      return None

  #-----------------------------------------------------------------------------

  def doDashExport(self):
    data = {}
    for key in self.snippets:
      snippet = self.snippets[key]
      data[key] = {}
      data[key]['title'] = snippet['title']
      for assetkey in snippet['rel_a']:
        asset = self.assets[assetkey]
        data[key]['data'] = "Note: %s\nPath: %s\n--\n\n%s" % (asset['note'].decode("utf-8", "replace"), asset['path'].decode("utf-8", "replace"), asset['content'].decode("utf-8", "replace"))
        if not data[key].has_key('syntax') and asset['syntax'] is not None:
          data[key]['syntax'] = asset['syntax']
      for tagkey in snippet['rel_t']:
        tag = self.tags[tagkey]
        data[key]['tags'] = tag['title']

      if not data[key].has_key('syntax'):
        data[key]['syntax'] = 'Standard'

    # iterx = data.itervalues()
    # print iterx.next()
   
  #-----------------------------------------------------------------------------

  def extToSyntax(self, ext):
    syntax = None
    if ext == 'c':
      syntax = 'C'
    elif ext == 'cc':
      syntax = 'C++'
    elif ext == 'config':
      syntax = 'Apache'
    elif ext == 'html':
      syntax = 'HTML'
    elif ext == 'java':
      syntax = 'Java'
    elif ext == 'json':
      syntax = 'JavaScript'
    elif ext == 'js':
      syntax = 'JavaScript'
    elif ext == 'm':
      syntax = 'Objective-C'
    elif ext == 'py':
      syntax = 'Python'
    elif ext == 'py':
      syntax = 'Ruby'
    elif ext == 'rb':
      syntax = 'Standard'
    elif ext == 'sql':
      syntax = 'SQL'
    elif ext == 'sh':
      syntax = 'Shell'
    elif ext == 'scpt':
      syntax = 'Applescript'
    elif ext == 'txt':
      syntax = 'Shell'

    return syntax

  #-----------------------------------------------------------------------------

  def doImport(self, file):
    fd = open(os.path.expanduser(file))
    data = fd.read()
    fd.close()
    doc = xml.dom.minidom.parseString(data)
    xobjects = doc.documentElement.getElementsByTagName('object')
    # print xobjects[0].toxml()

    for xobject in xobjects:
      # parse the object tag attributes
      xid = xobject.getAttribute('id')
      xtype = xobject.getAttribute('type')

      xdata = ""
      xpath = ""
      xsyntax = None
      xname = ""
      xnote = ""

      # parse the object attribute children
      attribs = xobject.getElementsByTagName('attribute')
      for attrib in attribs:
        bname = attrib.getAttribute('name')
        if bname == 'content':
          bdata = attrib.childNodes[0].nodeValue
          xdata = self.decode(bdata)
        if bname == 'path':
          xpath = attrib.childNodes[0].nodeValue
          ext = os.path.splitext(xpath)
          ext = ext[-1][1:]
          xsyntax = self.extToSyntax(ext)
        if bname == 'name':
          xname = attrib.childNodes[0].nodeValue
        if bname == 'notes':
          xnote = attrib.childNodes[0].nodeValue

      # parse the object relations children
      xrel_s = ""
      xrel_a = ""
      xrel_t = ""
      rels = xobject.getElementsByTagName('relationship')
      for rel in rels:
        dest = rel.getAttribute('destination')
        if dest == 'SNIPPET':
          xrel_s = rel.getAttribute('idrefs')
        if dest == 'ASSET':
          xrel_a = rel.getAttribute('idrefs')
        elif dest == 'TAG':
          xrel_t = rel.getAttribute('idrefs')

      # populate the data store
      if xtype == 'SNIPPET':
        if not self.snippets.has_key(xid):
          self.snippets[xid] = {}
        self.snippets[xid]['title'] = "-%s" % xname
        self.snippets[xid]['rel_a'] = xrel_a.split()
        self.snippets[xid]['rel_t'] = xrel_t.split()
      elif xtype == 'ASSET':
        if not self.assets.has_key(xid):
          self.assets[xid] = {}
        self.assets[xid]['content'] = xdata
        self.assets[xid]['path'] = xpath
        self.assets[xid]['note'] = xnote
        self.assets[xid]['syntax'] = xsyntax
        self.assets[xid]['rel_s'] = xrel_s.split()
        self.assets[xid]['rel_t'] = xrel_t.split()
      elif xtype == 'TAG':
        if not self.tags.has_key(xid):
          self.tags[xid] = {}
        self.tags[xid]['title'] = xname
        self.tags[xid]['rel_s'] = xrel_s.split()
        self.tags[xid]['rel_a'] = xrel_a.split()

    # stats
    print "snippets [%i]" % len(self.snippets)
    print "assets   [%i]" % len(self.assets)
    print "tags     [%i]" % len(self.tags)

    return 0

  def doDashDB(self, path):
    conn = sqlite3.connect(os.path.expanduser(path))
    c = conn.cursor()

    # Create table
    c.execute('''
      CREATE TABLE snippets
      (
        sid INTEGER PRIMARY KEY,
        title TEXT,
        body TEXT,
        syntax TEXT,
        usageCount INTEGER,
        FOREIGN KEY (sid) REFERENCES tagsIndex (sid) ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED
      )
      ''')

    c.execute('''
        CREATE TABLE tags
        (
            tid INTEGER PRIMARY KEY,
            tag TEXT UNIQUE,
            FOREIGN KEY (tid) REFERENCES tagsIndex (tid) ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED
        );
      ''')

    # c.execute('''
    #     CREATE UNIQUE INDEX sqlite_autoindex_tags_1 ON tags (tag)
    #   ''')

    c.execute('''
        CREATE TABLE tagsIndex
        (
            tid INTEGER,
            sid INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE smartTags
        (
            stid INTEGER PRIMARY KEY,
            name TEXT,
            query TEXT
        )
    ''')
    conn.commit()
    for tag in self.tags:
      print tag
      c.execute("INSERT INTO tags (tag) VALUES ('%s')", tag)
        
    conn.commit()
    conn.close()
  #-----------------------------------------------------------------------------

  def __init__(self, arg):
    try:
      self.snippets = {}
      self.assets = {}
      self.tags = {}
    except:
      print sys.exc_info()[0]

#===============================================================================

if __name__ == "__main__":
  base = Base(0)
  base.doImport("~/Dropbox/CodeBox.cbxml")
  base.doDashExport()
  base.doDashDB("~/Dropbox/snippetsExport.dash")

#===============================================================================

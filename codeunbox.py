#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# __author__ = "Marc Lavergne"
# __copyright__ = "Copyright 2013, Marc Lavergne"
# __license__ = "Modified BSD (http://directory.fsf.org/wiki/License:BSD_3Clause)"

import sys
import os

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

  def import(self, file):
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

      xname = ""
      xpath = ""
      xdata = ""

      # parse the object attribute children
      attribs = xobject.getElementsByTagName('attribute')
      for attrib in attribs:
        bname = attrib.getAttribute('name')
        if bname == 'content':
          bdata = attrib.childNodes[0].nodeValue
          xdata = self.decode(bdata)
        if bname == 'path':
          xpath = attrib.childNodes[0].nodeValue
        if bname == 'name':
          xname = attrib.childNodes[0].nodeValue

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
  base.import("~/Dropbox/CodeBox.cbxml")

#===============================================================================

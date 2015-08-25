#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of assemblage logging assistance classes and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

import logging
import re
import keyword

class Level(int):
  '''
  Subclasses int to associate a level value, with a NAME (often UPPER-CASE) and
  an attribute (method) name (defaults to lower-case version of name). The
  value defaults to None, indicating an auto-generated value should be chosen
  - these start at 1000 and increment with each use.
  '''
  __autoValue = 999
  @classmethod
  def __nextAutoValue(cls):
    '''
    Returns the next available auto-generated logging level value, starting 
    with 1000 for the first call then 1001 and so on.
    '''
    cls.__autoValue = cls.__autoValue + 1
    return cls.__autoValue
  @staticmethod
  def __isValidIdentifer(value):
    '''
    Return True if value is a valid Python identifier.
    Expects value to be a string.
    '''
    return re.match("[_A-Za-z][_a-zA-Z0-9]*$",value)

  def __new__(cls, name, attrName=None, value=None):
    '''
    Create a logging Level and register an associated name.
    Adds an object attribute for the attribute name value that can be used
    for class method attributes for example.
    If attrName is None (default) then the attribute name value will be 
    name.lower(). If value is None (default) then it is assigned automatically
    as the next available value of 1000 and above.
    '''
    if type(name) is not str:
      raise TypeError("Level.__new__: Expected name to be a string, not a '%s'" % str(type(name)))
    attrName = name.lower() if attrName==None else str(attrName)
    if (not Level.__isValidIdentifer(attrName)) or keyword.iskeyword(attrName):
      raise ValueError("Level.__init__: Expected attrName to be valid Python non-keyword identifier, got '%s'" % str(attrName))
    value = Level.__nextAutoValue() if value==None else value
    if type(value) is not int:
      raise TypeError("Level.__new__: Expected value to be integer, got '%s'" % str(type(value)))
    if value<0:
      raise ValueError("Level.__new__: Expected value to be positive got: %s" % str(value))
    self = super().__new__(cls,value)
    logging.addLevelName(value, name)
    self.__attrName = attrName
    return self

  def name(self):
    '''
    Returns the Level string name value as registered during creation.
    '''
    return logging.getLevelName(self)
  def attrName(self):
    '''
    Returns the Level attribute name value as set during creation.
    '''
    return self.__attrName

TRACE = Level("TRACE",value=15) # for messages between DEBUG and INFO in detail
OUTPUT = Level("OUTPUT",value=1) # for output usually for stdout

class Allow:
  '''
  Class for callable objects called with single logging level argument.
  Created from a similarly callable predicate that returns True or False
  depending on the passed level value.
  
  Returned value from call is True if level should be allowed, False if not.
  '''
  def __init__(self,predicate):
    '''
    Create from passed predicate that takes a logging level value and returns
    True or False depending on that value.
    '''
    self.__pred = predicate
  def __call__(self, level):
    '''
    Object call operator. Passed and logging level value and returns
    True or False True if level should be allowed, False if not - which is
    just the value returned from passing the level to the predicate used to
    create the Allow object with
    '''
#    print("Allow(self.__pred(%(l)d))=%(r)s"%{'l':level,'r':str(self.__pred(level))})
    return self.__pred(level)

class Deny:
  '''
  Class for callable objects called with single logging level argument.
  Created from a similarly callable predicate that returns True or False
  depending on the passed level value.
  
  Returned value from call is True if level should be allowed, False if not.
  '''
  def __init__(self,predicate):
    '''
    Create from passed predicate that takes a logging level value and returns
    True or False depending on that value.
    '''
    self.__pred = predicate
  def __call__(self, level):
    '''
    Object call operator. Passed and logging level value and returns
    True or False True if level should be allowed, False if not - which is
    the INVERSE of the value returned from passing the level to the predicate
    used to create the Deny object with - that is if the predicate returns True
    then the level is denied and so False should be returned.
    '''
    return not self.__pred(level)

class PerObjectLevelFilter:
  '''
  Logging filter allowing filtering by level on a per object basis.
  '''
  def __init__(self, *args):
    if len(args)>1 and type(args[0]) is dict:
      raise ValueError("PerObjectLevelFilter.__init__: expected single dict argument, got:'%s'" % str(args))
    self.__objLevelMap = {}
    if len(args):
      if type(args[0]) is dict:
        self.__objLevelMap = args[0]
      else:
        self.__objLevelMap = {None : args}
      for o,l in self.__objLevelMap.items():
        if not hasattr(l, '__iter__'):
          self.__objLevelMap[o] = [l]
        levelList = []
        for i in self.__objLevelMap[o]:
          ti = type(i)
      #    print("#### i is '%s'"%str(i))
          if i is None:
            pass
          elif ti is not Deny and ti is not Allow:
            raise ValueError("PerObjectLevelFilter.__init__: unexpected level specification of type '%s' in arguments, expected Allow, Deny or None"
                  % str(ti))
          levelList.append(i)
        self.__objLevelMap[o] = levelList
  def filter(self, record):
    args = record.args
#    print("FILTER#1: args:%s"%str(args))
    if not hasattr(args, '__iter__') or type(args) is str:
      args = [args]
    level = record.level
    if type(args) is dict:
      obj = args['object']   
    elif len(args)==1 and type(args[0]) is dict:
      obj = args[0]['object']
    elif len(args):
      obj = args[-1] # last argument, others presumably used in message formatting
    else:
      obj = None
#    print("FILTER#2: obj:%s in map: %s"%(str(obj),str(self.__objLevelMap)))
    if obj in self.__objLevelMap:
      levels = self.__objLevelMap[obj]
    elif type(obj) in self.__objLevelMap:
      levels = self.__objLevelMap[type(obj)]
    elif None in self.__objLevelMap:
      levels = self.__objLevelMap[None]
    else:
      levels = []
    allowed = False
#    print("FILTER#3: ## levels:%s"%levels)
    for levelTest in levels:
      action = type(levelTest)
    #  print("   >>>action:%s allowed:%s"%(str(action),str(allowed)))
      if action is Allow and not allowed: # allow previously denied level <query>
    #    print("   >>>Apply Allow()(%d)"%level)
        allowed = levelTest(level)
      elif action is Deny and allowed: # deny previously allowed level <query>
    #    print("   >>>Apply Deny()(%d)"%level)
        allowed = levelTest(level)
#    print("FILTER#4")
    return allowed

class Logger:
  @staticmethod
  def Name():
    '''
    Returns the name of the assemblage package logging.logger
    '''
    return "assemblage"
    
  '''
  Assemblage specific logging class wrapped around the Python logging support
  '''
  def __init__(self):
    '''
    Creates a logger for the assemblage package
    '''
    self.__logger = logging.getLogger(logger.Name())

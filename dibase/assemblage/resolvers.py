#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of function resolver classes and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .interfaces import ComponentBase
from .compound import Compound

import logging
import inspect
import sys

class CompositeResolver:
  '''
  A Function resolver that progresses through a list of individual resolver
  objects until a match is found or all resolvers have been consulted and no
  match could be located
  '''
  def __init__(self, *resolvers):
    '''
    Create a CompositeResolver for a sequence of Resolvers:
      cr = CompositeResolver([resolver1, resolver2,...])
    '''
    self.__resolvers = resolvers
  def resolve(self, fnName, object=None):
    '''
    Try to locate a function or method based on a function name and an 
    optional object which may be used in function / method resolution. 
    '''
    for r in self.__resolvers:
      fn = r.resolve(fnName, object)
      if fn:
        return fn
    return None

class ResolverFactory:
  '''
  Holds a class and a set of parameters to pass to __init__ on instance
  initialisation that are fixed for the duration of the factory.
  Instances of the resolver class are created by the create method that takes
  resolver instance initialisation argument values that vary  per instance.
  '''
  def __init__(self, resolverClass, **staticInitArgs):
    '''
    Creates a ResolverFactory instance from a class type object and a list
    of named arguments to pass to each created instance by the specific factory.
    '''
    self.__resolverClass = resolverClass
    self.__args = staticInitArgs
  def create(self, actionName, **dynamicInitArgs):
    '''
    Returns a newly created instance of the resolver class a factory creates.
    A list of additional named arguments may be passed whose values vary per
    resolver instance rather than per factory instance. The created object is
    passed the merged keyword argument map formed of the arguments given during
    factory initialisation and those given on resolver instances creation.
    '''
    args = self.__args.copy()
    args.update(dynamicInitArgs)
    return self.__resolverClass(actionName, **args)

class ResolutionPlan:
  '''
  Basically a ResolutionPlan is a composite ResolverFactory.
  Holds a sequence of ResolverFactory objects that produce a CompositeResolver
  on creation.
  '''
  def __init__(self, *factories, planResolverClass=CompositeResolver):
    self.__factories = factories
    self.__compositeResolverClass=planResolverClass
  def create(self, actionName, **dynamicInitArgs):
    '''
    Creates a sequence of resolvers from the sequences of factories, calling
    each factory's create method and passing the actionName and the 
    dynamicInitArg argument map to each - hence all resolvers share
    dynamicInitArg values and must be able to cope with them.
    Returns a CompositeResolver created from the produced resolver sequence.
    '''
    resolvers = []
    for f in self.__factories:
      resolvers.append( f.create(actionName, **dynamicInitArgs) )
    return self.__compositeResolverClass(*resolvers)

class ObjectResolver:
  '''
  Uses the object instance passed to the resolve method to look for an
  instance method named according to a pattern string given during
  initialisation, allowing substitution of the action and function names.
  '''
  def __init__(self, actionName, fnNamePattern="%(actionName)s_%(fnName)s", **unused):
    '''
    Requires an action name parameter and an optional additional fnNamePattern
    parameter specifying the method function name producing pattern value using
    Python string % formatting with named string format arguments actionName
    and fnName; defaults to the pattern: "%(actionName)s_%(fnName)s" producing
    method names of the form 'actionname_functionname'
    '''
    self.__actionName = actionName
    self.__pattern = fnNamePattern
  def resolve(self, fnName, object=None):
    '''
    Try to resolve the function specified by the fnName parameter as an
    instance method of the object parameter using the action name and
    pattern provided to the resolver's initialiser. Returns a callable wrapped
    object.method object or None if object has no such instance method.
    '''
    method = None
    if object:
      method = getattr( object
                      , self.__pattern%{'actionName':self.__actionName, 'fnName':fnName}
                      , None
                      )
    return method

class CallFrameScopeResolver:
  '''
  Resolves the name of a class class or static method. The class is searched for
  in the scope of a call frame specified as the number of frame from the current
  frame of the call to CallFrameScopeResolver._init__ during object creation.
  '''
  def __init__(self, actionName, frameNumber=4, fnNamePattern="%(fnName)s", clsNamePattern="%(actionName)s", **unused):
    '''
    Creates a call frame scope resolver from an action name,  a call frame
    number from the current call, defaulting to 4 (meaning the frame of the
    caller of the function creating a CallFrameScopeResolver object via a
    ResolverFactory and ResolutionPlan - e.g. the caller of an apply(action)
    method), a pattern for a class or static method name defaulting to the name
    of the function to resolve, and the name of the class the method belongs
    to, defaulting to the actionName parameter value.
    '''
    self.__actionName = actionName
    self.__frame = inspect.stack()[frameNumber][0]
    self.__fnPattern = fnNamePattern
    self.__clsPattern = clsNamePattern
  def __getNameInCallersScope(self, name):
    def getModuleFromFrame(frame):
      module_name = frame.f_globals['__name__']
      if module_name in sys.modules:
        module = sys.modules[module_name]
        if inspect.ismodule(module):
          return module
      return None
    def strmap(map, prefix='\n      '):
      mapstr = ''.join(['{{MAP TYPE : ',str(type(map)),'}}'])
      for k,v in map.items():
        mapstr = ''.join([mapstr,prefix,str(k),' : ',str(v),prefix, "  (type=",str(type(v)),')'])
      return mapstr
#    self.debug("LOOKING FOR CLASS '%(n)s' IN FRAME: %(f)d" %{'n':name, 'f':start_frame})
    if not self.__frame:
      return None
    flocals = self.__frame.f_locals
#    self.debug("FRAME  LOCALS:%s" % strmap(flocals))
#    self.debug("FRAME GLOBALS:%s" % strmap(self.__frame.f_globals))
    if name in flocals.keys():
      if inspect.isclass(flocals[name]):
        return flocals[name]
    if 'self' in flocals.keys(): # assume called from instance method:
      qualified_type = type(flocals['self'])
    elif 'cls' in flocals.keys(): # assume called from class method
      qualified_type = flocals['cls']
    else: # assume it is a module level function - includes class static methods
      module = getModuleFromFrame(self.__frame)
      if module:
        the_class = getattr(module, name, None)
        return the_class
      return None
    if inspect.isclass(qualified_type):
#      self.debug("Looking for '%(n)s' in scope: '%(t)s'"% {'n':name, 't':qualified_type})
      qualname = qualified_type.__qualname__
      qualname_parts = qualname.split('.')
#      self.debug("Qualified name parts: '%s'" % qualname_parts);
      if qualname_parts[-1]==name:
        return qualified_type # self value is the type we are looking for!
      the_class = getattr(qualified_type, name, None)
      if the_class:
        return the_class
      del qualname_parts[-1] # we just checked to see if name was part of the last element
#      self.debug("Qualified name parts to be processed:'%s'" % qualname_parts);
      obj = getModuleFromFrame(self.__frame)
      if obj:
#        self.debug("Adding part '%(p)s' (type '%(t)s')" % { 'p':obj, 't':type(obj)})
        obj_list = [obj]
        for part in qualname_parts:
          if part!='<locals>':
            obj = getattr(obj, part, None)
            if obj:
#              self.debug("Adding part '%(p)s' (type '%(t)s')" % { 'p':obj, 't':type(obj)})
              obj_list.append(obj)
            else:
#              self.debug("### FAILED finding object for part '%s' ###" % part)
              return None
        for obj in reversed(obj_list):
#          self.debug("Looking at part '%(p)s' (type '%(t)s')" % { 'p':obj, 't':type(obj)})
          if inspect.isclass(obj) or inspect.ismodule(obj):
#            self.debug("Processing part '%(p)s' (type '%(t)s')" % { 'p':obj, 't':type(obj)})
            the_class = getattr(obj, name, None)
            if the_class:
              return the_class
    return None

  def resolve(self, fnName, object=None):
    '''
    First tries to locate a class named according to the pattern given by the 
    clsNamePattern initialisation parameter in the scope of the call frame
    indicated by the frameNumber initialisation parameter. If such a class is
    returned then a function attribute is searched for named according to the
    pattern given by the fnNamePattern initialisation parameter, which if found
    is wrapped in a lambda expression that calls it passing the value of the
    object parameter. The initialisation actionName ans resolve fnName
    parameter values are used in expanding the class and function name patterns.
    '''
    clsName = self.__clsPattern%{'actionName':self.__actionName, 'fnName':fnName}
    actionClass = self.__getNameInCallersScope(clsName)
    if actionClass:
      mthdName = self.__fnPattern%{'actionName':self.__actionName, 'fnName':fnName}
      method = getattr(actionClass, mthdName, None)
      if method:
      #  self.debug("Found %(a)s.%(m)s"%{'a':clsName, 'm':mthdName})
        return lambda : method(object)
      else:
      #  self.debug("!! Method '%(c)s.%(m)s' not found !!" % {'c':clsName, 'm':mthdName})         
        pass
    else:
    #  self.debug("!! class '%s' not found !!" % clsName)
      pass
    return None

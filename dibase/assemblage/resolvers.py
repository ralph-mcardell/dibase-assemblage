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

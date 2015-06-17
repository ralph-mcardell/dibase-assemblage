#! /usr/bin/python3
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the Assemblage class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from interfaces import AssemblageBase

class Assemblage(AssemblageBase):
  '''
  A collection of top level elements, usually assemblage.Component (or
  derivative) objects, to which actions (strings) can be applied.
  
  Unlike a Component an Assemblage is unnamed and unconditionally applies
  actions to all its element components.
  
  Assemblage objects can have other Assemblage objects as elements, and can
  be used elements of Component objects. In these cases the assemblage acts
  as a pass-through layer for action application.
  '''
  @staticmethod
  def isiterable(object):
    '''
    Convenience function. Returns true if passed object is iterable. 
    Wrapper for hasattr(object, '__iter__').
    '''
    return hasattr(object, '__iter__')

  def __apply(self, object, action):
    '''
    Internal helper for apply method. Checks to see if object has a callable
    apply attribute. It is does then calls object.apply passing it action.
    Otherwise a warning is logged to the Assemblage logger.
    '''
    if hasattr(object, 'apply') and callable(getattr(object, 'apply')):
      object.apply(action)
    else:
      self.__logger.warning("Assemblage element has no 'apply' method (object=%(e)s)." % {'e':object})

  def __init__(self, plan):
    '''
    Extracts the Assemblage instance's logger and elements from the plan
    parameter object.
    
    The plan parameter is assumed to provide:
      - a logger instance method callable as plan.logger() 
        and returning a Python logging.logger object (or equivalent).
      - a topLevelElements instance method callable as
        plan.topLevelElements() and returning either a single element object
        or an iterable sequence of element objects. Element objects should
        provide an apply method and accept an action object - a string -
        as provided by assemblage.Component and derivatives.
    The plan parameter's requirements are met by assemblage.Blueprint objects.
    '''
    self.__logger = plan.logger()
    self.__digest_cache = plan.digestCache()
    self.__elements = plan.topLevelElements(self)

  def logger(self):
    '''
    Returns the assemblage logging.Logger object, provided by the plan object
    passed to Assemblage.__init__
    '''
    return self.__logger

  def digestCache(self):
    '''
    ##stub -- TBD##
    Returns a digest cache object.
    '''
    return self.__digest_cache

  def apply(self, action):
    '''
    Apply the passed action parameter to each object in the instance
    elements attribute. This is achieved simply by passing the action to
    each element's apply method. THe action parameter should be a string, or
    convertible to a string.
    The contents of the instance elements attribute (self.elements) should be
    either a single object or an iterable sequence of objects. Each such object
    needs to provide an apply method that accepts (other than the object's self
    argument) the action parameter string. A warning is logged for any
    element object that does not have a callable apply attribute.
    
    A warning is also logged if the elements attribute evaluates to False,
    i.e. is False, None, or an empty sequence, etc.
    '''
    if self.__elements:
      if Assemblage.isiterable(self.__elements):
        for e in self.__elements:
          self.__apply(e, action)
      else:
          self.__apply(self.__elements, action)
    else:
      self.__logger.warning("Assemblage is empty - no component elements to apply action to.")

#! /usr/bin/python3
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the Assemblage class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .interfaces import AssemblageBase
from .compound import Compound
import inspect

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

  def __init__(self, plan):
    '''
    Extracts the Assemblage instance's logger and elements from the plan
    parameter object.
    
    The plan parameter is assumed to provide:
      - a logger instance method callable as plan.logger() 
        and returning a Python logging.logger object (or equivalent).
      - a digestCache instance method callable as plan.digestCache() 
        and returning a dibase.assemblage.digestCache object (or equivalent).
      - a topLevelElements instance method callable as
        plan.topLevelElements() and returning either a single element object
        or an iterable sequence of element objects. Element objects should
        provide an apply method and accept an action object - a string -
        as provided by assemblage.Component and derivatives.
    The plan parameter's requirements are met by assemblage.Blueprint objects.
    '''
    self.__attributes = plan.attributes()
    elements = plan.topLevelElements()
    if not Assemblage.isiterable(elements):
      elements = [elements]
    self.__elements = Compound(self.__attributes,elements)

  def queryBeforeElementsActionsDone(self):
    '''
    Return False as Assemblage objects never perform action actions before
    passing the action application request on to their (top level) elements.
    '''
    return False
  def queryAfterElementsActionsDone(self):
    '''
    Return False as Assemblage objects never perform action actions after
    passing the action application request on to their (top level) elements.
    passing the action application request on to their (top level) elements.
    '''
    return False

  def logger(self):
    '''
    Returns the assemblage logging.Logger object, provided by the plan object
    passed to Assemblage.__init__
    '''
    return self.__attributes['__logger__']

  def digestCache(self):
    '''
    Returns a digest cache object.
    '''
    return self.__attributes['__store__']

  def _applyInner(self, action, scope):
    self.__attributes['__seen_elements__'] = []
    self.__elements._applyInner(action, scope)
    self.digestCache().writeBack()
    if self.__elements.queryAllAfterElementsActionsDone() and not self.__elements.queryAnyAfterElementsActionsDone():
      # the only time all action after actions done but not any were done
      # is if there are no elements with _applyInner methods to process
      self.logger().warning("Assemblage has no component elements to which"
                            " action '%(a)s' could be applied to."
                            % {'a':action}
                           )
  
  def apply(self, action):
    '''
    Apply the passed action parameter to each object in the instance
    elements attribute. This is achieved simply by passing the action to
    each element's apply method. The action parameter should be a string, or
    convertible to a string.
    The contents of the instance elements attribute (self.elements) should be
    either a single object or an iterable sequence of objects. Each such object
    needs to provide an _applyInner method that accepts (other than the
    object's self argument) the action parameter string, a list used to track
    seen elements for circular element processing detection and value
    indicating how far away in call frames the call is from the caller of this
    apply method used for resolving action classes. A warning is logged for any
    element object that does not have a callable apply attribute.
    
    A warning is also logged if the elements attribute evaluates to False,
    i.e. is False, None, or an empty sequence, etc.
    
    After an action has been applied any changed resource digests are written
    back to the Assemblage's digest cache.
    '''
    self._applyInner(action, inspect.stack()[1])

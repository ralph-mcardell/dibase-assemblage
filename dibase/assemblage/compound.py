#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the Compound class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .interfaces import CompoundBase
import logging
import inspect
import sys

class Compound(CompoundBase):
  '''
  Type implementing CompoundBase that represents a collection of component
  elements.
  '''
  def __init__(self, attributes, elements=[]):
    '''
    Create a Compound object from a list of ComponentBase (duck) type objects.
    Resets all state flags to False.
    '''
    self.__attributes = attributes
    self.__elements = elements
    self.reset()
    self.__logger = attributes['__logger__'] if '__logger__' in attributes\
                    else None
  def debug(self, message):
    if self.__logger and self.__logger.isEnabledFor(logging.DEBUG):
      self.__logger.debug(message)
  def error(self, message):
    if self.__logger and self.__logger.isEnabledFor(logging.ERROR):
      self.__logger.error(message)
  def warning(self, message):
    if self.__logger and self.__logger.isEnabledFor(logging.WARNING):
      self.__logger.warning(message)
  def reset(self):
    '''
    Resets all action application states to False.
    '''
    self.__anyBefore = False
    self.__allBefore = False
    self.__anyAfter = False
    self.__allAfter = False
  def queryAnyBeforeElementsActionsDone(self):
    '''
    Return true if any elements processed actions before processing their (sub-)
    element components. Returns false otherwise.
    '''
    return self.__anyBefore
  def queryAllBeforeElementsActionsDone(self):
    '''
    Return true if all elements processed actions before processing their (sub-)
    element components. Returns false otherwise.
    '''
    return self.__allBefore
  def queryAnyAfterElementsActionsDone(self):
    '''
    Return true if any elements processed actions after processing their (sub-)
    element components. Returns false otherwise.
    '''
    return self.__anyAfter
  def queryAllAfterElementsActionsDone(self):
    '''
    Return true if all elements processed actions after processing their (sub-)
    element components. Returns false otherwise.
    '''
    return self.__allAfter
  def apply(self, action):
    '''
    Applies action to all Component elements. Generally _applyInner should be
    called from a containing type such as a ComponentBase implementation.
    '''
    self.__attributes['__seen_elements__'] = []
    self._applyInner(action, inspect.stack()[1])
  def _applyInner(self, action, scope):
    '''
    Inner method used to apply function - not intended to be called by
    application code which should call apply. The _applyInner method is
    intended to be called on elements (co-)recursively generally from a
    containing object.
    Note: for an empty list of elements AnyXXX states will be False BUT
    AllXXX states with be True - as all of none did actions.
    '''
    self.reset()
    self.__allBefore = True
    self.__allAfter = True
    for element in self.__elements:
      self.debug("Processing Compound element: '%s'"%element)
      if hasattr(element, '_applyInner') and callable(getattr(element, '_applyInner')):
        element._applyInner(action, scope)
        if element.queryBeforeElementsActionsDone():
          self.__anyBefore = True
        else:
          self.__allBefore = False
        if element.queryAfterElementsActionsDone():
          self.__anyAfter = True
        else:
          self.__allAfter = False
      else:
        self.warning("Assemblage element has no '_applyInner' method (element=%(e)s)." % {'e':element})
  def __repr__(self):
    '''
    Returns a representation of the elements and the action done states
    '''
    return "%(c)s(ActionsDone:Before=%(b)s, After=%(a)s %(e)s)" \
          % {'c':self.__class__.__name__
            ,'b':'All ' if self.__allBefore else 'Any ' if self.__anyBefore else 'None'
            ,'a':'All ' if self.__allAfter else 'Any ' if self.__anyAfter else 'None'
            ,'e':self.__elements
            }


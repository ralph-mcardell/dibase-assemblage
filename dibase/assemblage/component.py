#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the Component class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .interfaces import ComponentBase
from .compound import Compound

import logging
import inspect
import sys

class Component(ComponentBase):
  '''
  Type that acts as the base element type in the assemblage package.

  Specific element types can subclass Component but should accept the core
  initialisation parameters of name, elements and logger (with those names) so
  as to be usable with assemblage.blueprint.Blueprint - usually passing them
  on to their Component superclass.

  Components support the relational operators and compare equal, less, greater
  etc. if their names are equal, greater, less etc. The string value of a
  component is its name.
  
  The main method is the apply method which applies an action (a string that is
  a valid Python identifier) to the component. The action is used to determine
  what action steps to perform and what those steps are.
  '''
  def __init__(self, name, attributes, elements=[], logger=None):
    self.__name = name
    self.__attributes = attributes
    self.__elements = Compound(attributes,elements)
    if type(logger) is logging.Logger:
      self.__logger = logger  
    elif type(logger) is str:
      self.__logger = logging.getLogger(logger)
    elif '__logger__' in attributes and attributes['__logger__']:
      self.__logger = attributes['__logger__']
    else:
      self.__logger = logging.getLogger()
    self.debug("Created %s"%repr(self))
    self.reset()

  def __repr__(self):
    '''
    Note: representation ignores __logger attribute.
    Return a representation that if evaluated creates object that logs to the 
    root logger.
    '''
    return "%(c)s{name=%(n)s,elements=%(e)s}" % {'c':self.__class__.__name__,'n':self.__name,'e':self.__elements}
  def __str__(self):
    return self.__name
  def __hash__(self):
    return hash(self.__name)
  def __lt__(self, other):
    return str(self) < str(other)
  def __le__(self, other):
    return str(self) <= str(other)
  def __eq__(self, other):
    return str(self) == str(other)
  def __ne__(self, other):
    return str(self) != str(other)
  def __gt__(self, other):
    return str(self) > str(other)
  def __ge__(self, other):
    return str(self) >= str(other)

  def __log_message(self, message, frame=1):
    callerframe = inspect.getouterframes(inspect.currentframe(),3)
    return " [%(c)s.%(f)s]\n   %(m)s" % {'c':repr(self),'f':callerframe[frame][3], 'm':message}

  def debug(self, message):
    if self.__logger.isEnabledFor(logging.DEBUG):
      self.__logger.debug(self.__log_message(message,2))

  def error(self, message):
    if self.__logger.isEnabledFor(logging.ERROR):
      self.__logger.error(message)
 
  def _applyInner(self, action, resolver):
    def resolve_and_call_function(action, action_method_name, resolver):
      func = resolver.resolve(action_method_name, self)
      return func and func()
    def query_do_before_elements_actions(action, resolver):
      return resolve_and_call_function(action, 'queryDoBeforeElementsActions', resolver)
    def query_do_after_elements_actions(action, resolver):
      return resolve_and_call_function(action, 'queryDoAfterElementsActions', resolver)
    def query_process_elements( action, resolver):
      return resolve_and_call_function(action, 'queryProcessElements', resolver)
    def do_before_elements_actions( action, resolver):
      resolve_and_call_function(action, 'beforeElementsActions', resolver)
    def do_after_elements_actions(action, resolver):
      resolve_and_call_function(action, 'afterElementsActions', resolver)

    self.debug("Component attributes: '%s'" % self.__attributes)
    self.reset()
    if self in self.__attributes['__seen_elements__']:
      raise RuntimeError( self.__log_message( "Circular reference: already tried to "
                                              "apply action '%(a)s' to element '%(e)s'"
                                              % {'e':str(self), 'a':action}
                                            )
                        )
    self.__attributes['__seen_elements__'].append(self)
    self.debug("apply('%s'): Querying do before actions" % action)
    if query_do_before_elements_actions(action, resolver):
      self.debug("Passed check, doing before actions")
      do_before_elements_actions(action, resolver)
      self.__beforeDone = True
    self.debug("apply('%s'): Querying process elements" % action)
    if query_process_elements(action, resolver):
      self.debug("Passed check, processing elements")
      self.__elements._applyInner(action, resolver)
    self.debug("apply('%s'): Querying do after actions" % action)
    if query_do_after_elements_actions(action, resolver):
      self.debug("Passed check, doing after actions")
      do_after_elements_actions(action, resolver)
      self.__afterDone = True
    self.__attributes['__seen_elements__'].remove(self)

  def reset(self):
    self.__beforeDone = False
    self.__afterDone = False
  def queryBeforeElementsActionsDone(self):
    '''
    Return true if component processed actions before processing (sub-)
    element components. Returns false otherwise.
    '''
    return self.__beforeDone
  def queryAfterElementsActionsDone(self):
    '''
    Return true if component processed actions after processing (sub-)
    element components. Returns false otherwise.
    '''
    return self.__afterDone

  def apply(self, action):
    '''
    Apply an action to an element.
    action is expected to be a string that is a valid Python identifier.
    It is used to locate functions used in the application of an action to
    a Component element.
    There are 5 functions that define how an action is processed by a
    Component: 3 control what processing occurs and 2 perform processing:
      queryDoBeforeElementsActions: 
      Returns True if processing actions are to be performed before (possibly)
      calling apply with the action for each of the Component's elements.

      queryProcessElements:
      Returns True if apply with the action should be called for each of the
      Component's elements.

      queryDoAfterElementsActions:
      Returns True if processing actions are to be performed after apply was
      potentially called with the action for each of the Component's elements.
  
      beforeElementsActions:
      Actions that should be performed if necessary before applying the action
      to the Component's elements.

      afterElementsActions:
      Actions that should be performed if necessary after applying the action
      to the Component's elements.

    Appropriate functions or methods are resolved using a resolver created from
    the '__resolution_plan__' attribute object (a resolvers.ResolutionPlan
    - or compatible type - object).
    '''
    self.__attributes['__seen_elements__'] = []
    resolver = self.__attributes['__resolution_plan__'].create(action)
    self._applyInner(action, resolver)
  def digest(self):
    '''
    Intended to be overridden.
    Return a fixed length sequence of bytes representing the state of any
    resource(s) managed by a Component element It is used for detection of
    changes to resources in conjunction with a DigestCache (or similar) object.
    As the base Component type does not manage any sort of resource it simply
    returns a fixed 8-byte (64-bit) byte sequence.
    '''
    return b'Componen'
  def doesNotExist(self):
    '''
    Intended to be overridden.
    Returns True if the resource a Component represents - such as a file or
    service process - does not exist.
    The base Component implement always returns True as it has no associated
    resource to exist.
    '''
    self.debug("Stating that Component does not exist")
    return True
  def isOutOfDate(self):
    '''
    Returns True if the resource a Component or successor element represents 
    - such as a file or service process - is out of date.
    If the Component has child elements then they are iterated over passing
    the request on to each and latching any True result. Otherwise the
    Component is a leaf element with no child elements and the result of
    calling the Component's hasChanged method is returned.
    
    That is, the only elements for which change checks need to be performed are
    childless leaf elements as it is assumed these are changed externally to
    the assemblage whereas all other elements presumably have actions that
    re-create them from their child elements.
    '''
    self.debug("Checking if Component is out of date")
    result = False
    # out of date if any (sub-)element was processed
    # temporary fix during refactoring transitioning.
    if  self.__elements.queryAnyBeforeElementsActionsDone()\
     or self.__elements.queryAnyAfterElementsActionsDone():
      result = True
    elif self.__elements.queryAllAfterElementsActionsDone():
    # If after processing the __elements Compound did not have any
    # elements with actions processed but all elements had actions
    # processed then it implies there are NO elements to process
      result = self.hasChanged()
    return result
  def hasChanged(self):
    '''
    Passes self onto the assemblage digest cache which compares
    current Component.digest() value with the previous cached/stored value.
    '''
    has_changed = self.__attributes['__store__'].updateIfDifferent(self)\
                  if '__store__' in self.__attributes else False
    self.debug("Checking if Component has changed: %s"%has_changed)
    return has_changed

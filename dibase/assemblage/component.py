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
    self.__elements = elements
    if type(logger) is logging.Logger:
      self.__logger = logger  
    elif type(logger) is str:
      self.__logger = logging.getLogger(logger)
    elif '__logger__' in attributes and attributes['__logger__']:
      self.__logger = attributes['__logger__']
    else:
      self.__logger = logging.getLogger()
    self.debug("Created %s"%repr(self))
  def __repr__(self):
    '''
    Note: representation ignores __logger attribute.
    Return a representation that if evaluated creates object that logs to the 
    root logger.
    '''
    return "%(c)s(name=%(n)s,elements=%(e)s)" % {'c':self.__class__.__name__,'n':self.__name,'e':self.__elements}
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

  def elementAttribute(self, id, name, default=AttributeError):
    if (type(id) is not int) or id<0 or id>=len(self.__elements):
      if default is AttributeError:
        raise IndexError( self.__log_message( "id %(i)s is not an integer"
                                             " or out of range [0,%(e)d]"
                                              % {'i':str(id)
                                                , 'e':len(self.__elements)-1}
                                            )
                        )
      else:
        return default
    return getattr(self.__elements[id],name) if default is AttributeError\
            else getattr(self.__elements[id],name,default)

  def __log_message(self, message, frame=1):
    callerframe = inspect.getouterframes(inspect.currentframe(),3)
    return " [%(c)s.%(f)s]\n   %(m)s" % {'c':repr(self),'f':callerframe[frame][3], 'm':message}
    
  def debug(self, message):
    if self.__logger.isEnabledFor(logging.DEBUG):
      self.__logger.debug(self.__log_message(message,2))
    
  def error(self, message):
    if self.__logger.isEnabledFor(logging.ERROR):
      self.__logger.error(message)

#  def assemblage(self):
#    return self.__assemblage

  def __get_class_in_callers_scope(self, name, start_frame=2):
    def get_module_from_frame(frame):
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
    frames = inspect.stack()
    if len(frames) < start_frame:
      return None
    frame = frames[start_frame][0]
    flocals = frame.f_locals
#    self.debug("FRAME  LOCALS:%s" % strmap(flocals))
#    self.debug("FRAME GLOBALS:%s" % strmap(frame.f_globals))
    if name in flocals.keys():
      if inspect.isclass(flocals[name]):
        return flocals[name]
    if 'self' in flocals.keys(): # assume called from instance method:
      qualified_type = type(flocals['self'])
    elif 'cls' in flocals.keys(): # assume called from class method
      qualified_type = flocals['cls']
    else: # assume it is a module level function - includes class static methods
      module = get_module_from_frame(frame)
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
      obj = get_module_from_frame(frame)
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

  def __get_class_qualname_in_callers_scope(self, name, start_frame=2):
    the_class = get_class_in_callers_scope(name, start_frame+1) # exclude our frame
    if the_class:
#      self.debug("   Returning '%s'" % '.'.join([the_class.__module__,the_class.__qualname__]))
      return '.'.join([the_class.__module__,the_class.__qualname__])
    return None
  
  def __resolver(self,action, action_method_name, callers_frame=2):
      self.debug("apply('%(a)s): Resolving function '%(f)s'"
                         % {'a':action,'f':action_method_name})
      self_method_name = ''.join([action,'_', action_method_name])
      method = getattr(self, self_method_name, False)
      if method:
        self.debug("Found method 'self.%s'"%self_method_name)
        return method
      else:
        action_class = self.__get_class_in_callers_scope(action,callers_frame+1)
        if action_class:
          method = getattr(action_class, action_method_name, False)
          if method:
            self.debug("Found %(a)s.%(m)s"%{'a':action, 'm':action_method_name})
            return lambda : method(self)
          else:
            self.debug("!! Method '%(c)s.%(m)s' not found !!" % {'c':action, 'm':action_method_name})         
        else:
          self.debug("!! class '%s' not found !!" % action)
        return False
 
  def _applyInner(self, action, seen_components, callers_frame=5):
    def resolve_and_call_function(action, action_method_name, callers_frame=3):
      func = self.__resolver(action, action_method_name, callers_frame+1)
      return func and func()
    def query_do_before_elements_actions(action, callers_frame=4):
      return resolve_and_call_function(action, 'queryDoBeforeElementsActions', callers_frame+1)
    def query_do_after_elements_actions(action, callers_frame=4):
      return resolve_and_call_function(action, 'queryDoAfterElementsActions', callers_frame+1)
    def query_process_elements( action, callers_frame=4):
      return resolve_and_call_function(action, 'queryProcessElements', callers_frame+1)
    def do_before_elements_actions( action, callers_frame=4):
      resolve_and_call_function(action, 'beforeElementsActions', callers_frame+1)
    def do_after_elements_actions(action, callers_frame=4):
      resolve_and_call_function(action, 'afterElementsActions', callers_frame+1)

    if self in seen_components:
      raise RuntimeError( self.__log_message( "Circular reference: already tried to "
                                              "apply action '%(a)s' to element '%(e)s'"
                                              % {'e':str(self), 'a':action}
                                            )
                        )
    seen_components.append(self)
    self.debug("apply('%s): Querying do before actions" % action)
    callers_frame = callers_frame + 1
    if query_do_before_elements_actions(action, callers_frame):
      self.debug("Passed check, doing before actions")
      do_before_elements_actions(action, callers_frame)
    self.debug("apply('%s): Querying process elements" % action)
    if query_process_elements(action, callers_frame):
      self.debug("Passed check, processing elements")
      for element in self.__elements:
        self.debug("Processing element:'%s'"%element)
        element._applyInner(action, seen_components, callers_frame)
    self.debug("apply('%s): Querying do after actions" % action)
    if query_do_after_elements_actions(action, callers_frame):
      self.debug("Passed check, doing after actions")
      do_after_elements_actions(action, callers_frame)
    seen_components.remove(self)

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

    Appropriate method functions are looked for first as instance methods of
    the Component (defined by a Component subclass), and have the action name
    and an underscore prefixed to the names shown above - so 
    'queryProcessElements' for action 'doit' would have the name
    'doit_queryProcessElements'. Such functions are not passed any parameters
    other than the self parameter.

    If no such method is located for the (action, function) pair then a class
    having the same name as the action is searched for in the caller's scope,
    starting with calling function local classes and moving out through any
    (nested) class scopes to the caller's module level. If such a class is
    found then methods of the names shown above a searched for and are expected
    to be either class or static methods taking (other than the cls parameter
    for class methods) only the Component as a parameter.
    '''
    self._applyInner(action, [], callers_frame=2)
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
    if self.__elements:
      for e in self.__elements: # intentionally touch all elements
        result = e.isOutOfDate() or result
    else:
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

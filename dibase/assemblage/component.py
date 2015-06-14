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

import logging
import inspect
import sys

class Component:
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
  what action steps to perform and what those steps are. The apply method uses
  the action to call a function at 5 points in processing, 3 boolean query
  functions and two action-step performing functions. If a function is not
  located for an action then the default behaviour is to evaluate to False
  for the query functions and do nothing for the action step function.  The
  outline of apply processing is:

    if query_do_before_elements_actions(the_action):
      do_before_elements(the_action)
    if query_process_elements(the_action):
      for each of the component's elements, e:
        e.apply(the_action)
    if query_do_after_elements_actions(the_action):
      do_after_elements(the_action)
 
  The functions supporting an action are searched for using an action function
  resolver. The default resolver looks first for the functions as method
  attributes of the component object with the names:
    <action name>_query_do_before_elements_actions
    <action name>_query_do_after_elements_actions
    <action name>_query_process_elements_actions
    <action name>_before_elements_actions
    <action name>_after_elements_actions
  where <action name> is the action name string - 'build' or 'service_up' for
  example. The methods would be defined in Component subclasses. No
  parameters, other than self if the methods are instance methods, are passed
  to the functions.

  If a method function is not found then the default resolver checks up the
  caller's scope, ignoring function local scopes other than that of the caller,
  for an action class with the same name as the action. If such a class is
  found class or static methods with the names:
    query_do_before_elements_actions
    query_do_after_elements_actions
    query_process_elements_actions
    before_elements_actions
    after_elements_actions
  are looked for and if found called with the self value of the calling
  component.
  '''
  def __init__(self, name, elements=[], logger=None):
    self.__name = name
    self.__elements = elements
    if type(logger) is logging.Logger:
      self.__logger = logger  
    else:
      self.__logger = logging.getLogger(logger)
    self.__logger.debug("Created %s"%repr(self))
  def __repr__(self):
    '''
    Note: representation ignores __logger attribute.
    Return a representation that if evaluated creates object that logs to the 
    root logger.
    '''
    return "Container(name=%(n)s,elements=%(e)s)" % {'n':self.__name,'e':self.__elements}
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

  def __get_class_in_callers_scope(self, name, start_frame=2):
    def get_module_from_frame(frame):
      module_name = frame.f_globals['__name__']
      if module_name in sys.modules:
        module = sys.modules[module_name]
        if inspect.ismodule(module):
          return module
      return None
  
    frames = inspect.stack()
    if len(frames) < start_frame:
      return None
    frame = frames[start_frame][0]
    flocals = frame.f_locals
#    self.__logger.debug("FRAME  LOCALS:",strmap(flocals))
#    self.__logger.debug("FRAME GLOBALS:",strmap(frame.f_globals))
    if name in flocals.keys():
      if inspect.isclass(flocals[name]):
        return flocals[name]
    if 'self' in flocals.keys(): # assume called from instance method:
      qualified_type = type(flocals['self'])
    elif 'cls' in flocals.keys(): # assume caled from class method
      qualified_type = flocals['cls'] ## cls _is a_ class!
    else: # assume it is a module level function - includes class static methods
      module = get_module_from_frame(frame)
      if module:
        the_class = getattr(module, name, None)
        return the_class
      return None
    if inspect.isclass(qualified_type):
      self.__logger.debug("LOOKING FOR '%(n)s' in scope: '%(t)s'"% {'n':name, 't':qualified_type})
      qualname = qualified_type.__qualname__
      qualname_parts = qualname.split('.')
#      self.__logger.debug('QUALIFIEDNAME PARTS:',qualname_parts);
      if qualname_parts[-1]==name:
        return qualified_type # self value is the type we are looking for!
      the_class = getattr(qualified_type, name, None)
      if the_class:
        return the_class
      del qualname_parts[-1] # we just checked to see if name was part of the last element
#      self.__logger.debug('QUALIFIEDNAME PARTS TO BE PROCESSED:',qualname_parts);
      obj = get_module_from_frame(frame)
      if obj:
#        self.__logger.debug('   Adding part', obj, '(type ',type(obj),')')
        obj_list = [obj]
        for part in qualname_parts:
          if part!='<locals>':
            obj = getattr(obj, part, None)
            if obj:
#              self.__logger.debug('   Adding part', obj, '(type ',type(obj),')')
              obj_list.append(obj)
            else:
#              self.__logger.debug("###Failed finding object for part '", part,"'", sep='')
              return None
        for obj in reversed(obj_list):
#          self.__logger.debug('   Looking at part', obj, '(type ',type(obj),')')
          if inspect.isclass(obj) or inspect.ismodule(obj):
#            self.__logger.debug('   Processing part', obj, '(type ',type(obj),')')
            the_class = getattr(obj, name, None)
            if the_class:
              return the_class
    return None

  def __get_class_qualname_in_callers_scope(self, name, start_frame=2):
    the_class = get_class_in_callers_scope(name, start_frame+1) # exclude our frame
    if the_class:
#      self.__logger.debug("   Returning '", '.'.join([the_class.__module__,the_class.__qualname__]),"'")
      return '.'.join([the_class.__module__,the_class.__qualname__])
    return None
  
  def __resolver(self,action, action_method_name, callers_frame=2):
      self.__logger.debug("Component('%(n)s').apply('%(a)s): Resolving function '%(f)s'"
                         % {'n':str(self), 'a':action,'f':action_method_name})
      self_method_name = ''.join([action,'_', action_method_name])
      method = getattr(self, self_method_name, False)
      if method:
        self.__logger.debug("  -- Found method 'self.%s'"%self_method_name)
        return method
      else:
        action_class = self.__get_class_in_callers_scope(action,callers_frame)
        if action_class:
          method = getattr(action_class, action_method_name, False)
          self.__logger.debug("  -- Found %(a)s.%(m)s"%{'a':action, 'm':action_method_name})
          return lambda : method(self)
        else:
          self.__logger.debug("  !! class '%s' not found !!"%action)
          return False
 
  def __apply_inner(self, action, seen_components, callers_frame=5):
    def resolve_and_call_function(action, action_method_name, callers_frame=3):
      func = self.__resolver(action, action_method_name, callers_frame)
      return func and func()
    def query_do_before_elements_actions(action, callers_frame=4):
      return resolve_and_call_function(action, 'query_do_before_elements_actions', callers_frame)
    def query_do_after_elements_actions(action, callers_frame=4):
      return resolve_and_call_function(action, 'query_do_after_elements_actions', callers_frame)
    def query_process_elements( action, callers_frame=4):
      return resolve_and_call_function(action, 'query_process_elements', callers_frame)
    def do_before_elements_actions( action, callers_frame=4):
      resolve_and_call_function(action, 'before_elements_actions', callers_frame)
    def do_after_elements_actions(action, callers_frame=4):
      resolve_and_call_function(action, 'after_elements_actions', callers_frame)

    if self in seen_components:
      raise RuntimeError("Circular reference: already tried to apply action '%(a)s' to element '%(e)s'"
                        % {'e':str(self), 'a':action}
                        )
    seen_components.append(self)
    self.__logger.debug("Component('%(n)s').apply('%(a)s): Querying do before actions"
                       % {'n':str(self), 'a':action})
    if query_do_before_elements_actions(action, callers_frame):
      self.__logger.debug("  -- Passed check, doing before actions")
      do_before_elements_actions(action, callers_frame)
    self.__logger.debug("Component('%(n)s').apply('%(a)s): Querying process elements"
                        % {'n':str(self), 'a':action})
    if query_process_elements(action, callers_frame):
      self.__logger.debug("  -- Passed check, processing elements")
      for element in self.__elements:
        self.__logger.debug("  -- Processing element:'%s'"%element)
        element.__apply_inner(action, seen_components, callers_frame+1)
    self.__logger.debug("Component('%(n)s').apply('%(a)s): Querying do after actions"
                        % {'n':str(self), 'a':action})
    if query_do_after_elements_actions(action, callers_frame):
      self.__logger.debug("  -- Passed check, doing after actions")
      do_after_elements_actions(action, callers_frame)
    seen_components.remove(self)

  def apply(self, action):
    self.__apply_inner(action, [], callers_frame=6)

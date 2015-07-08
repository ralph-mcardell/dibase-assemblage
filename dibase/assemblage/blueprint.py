#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the Blueprint class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .interfaces import AssemblagePlanBase
import logging
import sys
import inspect

class Blueprint(AssemblagePlanBase):
  '''
  Provide blueprint plans for assemblages.
  Instances can be passed to assemblage.Assemblage constructor to create
  a set of element acyclic graphs of assemblage.Components or similar to
  which actions can be applied.
  
  Two attributes are managed by Blueprint:
    - logging objects - of the Python library logging.Logger type
    - elements
  A logger can be set on a Blueprint object at any time with the setLogger
  method after which it will be returned by the logger method and passed to any
  element on creation if no specific logger has been specified for the element.
  If no logger is set when one is required then a default is created and used.
  
  Elements can be added with the addElements method and top level elements
  retrieved by calling the topLevelElements method. When elements are
  added only their specification is stored. Calling topLevelElements causes the
  current element specification data to be used to create the element objects
  from their specifications, associating child elements with their parents -
  note that a child element can be referenced by multiple parents. Finally
  which elements are the top level root elements (elements having no parents)
  are determined and returned.
  '''
  class __ElementSpec:
    '''
    Used to hold specification data for elements between being added to a
    Blueprint and being used to create a set of top level elements representing
    the roots of acyclic graphs of elements.
    '''
    def __init__(self, name, kind, elements, logger, **kwargs):
      '''
      Stores the passed data for later use.
      '''
      self.name = name
      self.kind = kind
      self.elements = elements
      self.logger = logger
      self.args = kwargs

  class __ElementView:
    '''
    Type for objects passed to names and (sub-)elements creation functions
    (or other callable type).
    Interface takes its style from the Python library configparser.ConfigParser
    class' section, has_section, has_option, option methods.
    '''
    def __init__(self, by_group):
      '''
      Initialised by Blueprint.addElement passing the object's internal
      collection of added elements keyed on their group name.
      '''
      self.__elements_by_group = {}
      for k,v in by_group.items():
        self.__elements_by_group[k] = []
        for es in v:
          self.__elements_by_group[k].append(es.name)
    def groups(self):
      '''
      Returns a list of group names currently known to a Blueprint object.
      '''
      return self.__elements_by_group.keys()
    def has_group(self, group):
      '''
      Returns True if group name passed in group is currently known to
      a Blueprint object, False if it is not.
      '''
      return group in self.groups()
    def elements(self, group):
      '''
      Returns a list of element names currently known for the group name
      passed in group. Returns an empty list if the group name is unknown.
      '''
      return self.__elements_by_group[group] if self.has_group(group) else []
    def has_element(self, group, element):
      '''
      Returns True if the element name passed in element is currently a member 
      of the group name passed in group. Returns False if group or element are
      unknown.
      '''
      return self.has_group(group) and element in self.elements(group)

  def __init__(self):
    '''
    Initialise an empty Blueprint object having no logger or elements.
    '''
    self.__attributes = { '__logger__' : None
                        , '__store__'  : None
                        }
    self.__element_specs_by_group = {}
    self.__element_specs_by_name = {}
    self.__non_root_elements = set()

  def __set_default_logger(self):
    '''
    Internal method to set a default logging.Logger to use should there not
    have been one set at the time the logger method is called.
    '''
    log = logging.getLogger("assemblage.default")
    log.propagate = False
    if not log.hasHandlers():
      loghdr = logging.StreamHandler(stream=sys.stdout)
      loghdr.setLevel(logging.DEBUG)
      formatter = logging.Formatter('%(levelname)s: %(message)s')
      loghdr.setFormatter(formatter)
      log.addHandler(loghdr)
      log.setLevel(logging.INFO)
    self.__attributes['__logger__'] = log

  def attributes(self):
    '''
    Returns the attributes map - intended primarily to be used by Assemblage
    __init__ to get a reference to the map.
    '''
    return self.__attributes

  def logger(self):
    '''
    Returns the logging.Logger instance associated with this Blueprint. If
    when called there is no associated logger then a default one is provided.
    '''
    if not self.__attributes['__logger__']:
      self.__set_default_logger()
    return self.__attributes['__logger__']

  def setLogger(self, logger):
    '''
    Set a pre-configured logging.Logger (or equivalent) object to be the 
    logger object currently associated with a Blueprint object.
    '''
    self.__attributes['__logger__'] = logger
    return self

  def setDigestCache(self, digest_cache):
    '''
    Set a value for the assemblage.interfaces.DigestCacheBase compatible
    element resource digest cache used to support resource change detection.
    '''
    self.__attributes['__store__'] = digest_cache
    return self

  def digestCache(self):
    '''
    Return the value of the previously set assemblage.interfaces.DigestCacheBase
    compatible object.
    '''
    return self.__attributes['__store__']

  def topLevelElements(self):
    '''
    Returns a list of top level root elements to which actions may be applied.
    The list might be empty. Top level elements are each roots of an acyclic 
    network of elements - that is elements may share child elements, but a
    child element cannot have an ancestor as a child. The assemblage parameter
    is passed to all elements constructed as the assemblage argument.
    '''

    def add_element_from_specification(specification, elements, seen_elements):
      '''
      Internal helper method for topLevelElememnts. Creates an element. 
      First recursively creates any of its (sub-)elements that do not yet exist.
      Passed the specification to use to create the element and an elements
      'element name:element' dictionary to hold newly created elements.
      seen_elements keeps track of elements already seen by this sequence of
      recursive calls. topLevelElements starts a new sequence of calls by
      passing seen_elements as an empty list.
      '''
      subelements = []
      seen_elements.append(specification.name)
      for subname in specification.elements:
        if subname in seen_elements:
          raise RuntimeError("Circular reference: Child element '%(c)s' is also an ancestor of '%(a)s'"
                            % {'c':subname, 'a':specification.name}
                            )
        if subname in elements:
          subelements.append(elements[subname])
        else: # element not created yet - go make it
          if subname in self.__element_specs_by_name:
            add_element_from_specification(self.__element_specs_by_name[subname], elements, seen_elements)
            subelements.append(elements[subname])
          else:
            raise RuntimeError("Element undefined: No element added with name '%(e)s'" % {'e':subname})
      if inspect.isclass(specification.kind):
        elements[specification.name] = \
          (specification.kind(name=specification.name,attributes=self.__attributes 
          ,elements=subelements,logger=specification.logger,**specification.args))
      else:
        elements[specification.name] = specification.kind
      seen_elements.remove(specification.name)
    elements = {}
    for es in self.__element_specs_by_name.values():
      if not es.logger:
        es.logger = self.logger()
      if es.name not in elements.keys():
        add_element_from_specification(es, elements, seen_elements=[])
    tlelements = []
    for ename, element in elements.items():
      if ename not in self.__non_root_elements:
        tlelements.append(element)
    return tlelements

  def addElements(self, names, kind, group='', elements=[], logger=None, **kwargs):
    '''
    Add one or more element descriptions to a Blueprint instance.
    The required names parameter may be a string, a list of strings, or a
    function (or other callable entity) that returns a list of names.
    The kind parameter, also required, is a class object that is to be
    used to create instances of the elements to be added.
    The optional group parameter can be used to associate the elements to be
    created with a group name. If not given then the elements will become
    members of the group with the empty name.
    The optional elements parameter names elements that are parts this element
    requires/depends on. Like the names parameter it may be a single string,
    or a list of strings - in which case all added elements will have the same
    dependent elements. It may also be a list of lists - with each inner list
    corresponding to the elements for the element with the name in the
    same position in the names parameter's list. A dictionary may also be used
    in which the key is name to which the elements apply and the value is a
    string or list naming one or more elements. Finally, like the names
    parameter, a function may be provided that returns the (sub-)elements
    for each element.
    The logger argument allows elements to use a specific logging.Logger.
    If not provided the elements will be passed the logger set for Blueprint
    object at the time topLevelElements creates them.
    Any other parameters provided by the kwargs parameter are passed as
    additional creation parameters to element object construction. AT this time
    all elements created by a single addElements call have to use the same
    additional argument values.
    
    The functions that may be provide for names and elements argument values
    take a type that allows access to names of elements in groups (see the
    Blueprint.__ElementView class). They may return any value that could be
    passed to the names or elements parameters - including another callable
    function. This can be done repeatedly but it is suggested that more than a
    few recursions is probably not useful.
    A RuntimeError is raised if an element (specification) with a given name
    has already been added.
    '''
    def process_kwargs(name, index, kwargs):
      outargs = {}
      for k,v in kwargs.items():
        if type(v) is list:
          outargs[k] = v[index]
        elif type(v) is dict:
          outargs[k] = v[name]
        else:
          outargs[k] = v
      return outargs
    def process_elements(name,index,elements):
      outargs = []
      if type(elements) is dict:
        outargs = elements[name]
      elif type(elements) is list and len(elements) and type(elements[0]) is list:
        outargs = elements[index]
      else:
        outargs = elements
      return [outargs] if type(outargs) is str else outargs
    def resolve_to_collection(value):
      if type(value) is str:
        return [value]
      elif callable(value):
        return resolve_to_collection(value(Blueprint.__ElementView(self.__element_specs_by_group)))
      else:
        return value

    names = resolve_to_collection(names)
    elements = resolve_to_collection(elements)
    nm_index = 0
    for name in names:
      if name in self.__element_specs_by_name:
        raise RuntimeError("Duplicate element: there is already an element called '%(n)s'" % {'n':name})
      this_element_kwargs = process_kwargs(name,nm_index,kwargs)
      this_element_elements = process_elements(name,nm_index,elements)
      new_spec = Blueprint.__ElementSpec(name, kind, this_element_elements, logger, **this_element_kwargs)
      self.__element_specs_by_name[name] = new_spec
      if group not in self.__element_specs_by_group:
        self.__element_specs_by_group[group] = []
      self.__element_specs_by_group[group].append(new_spec)
      for e in this_element_elements:
        if e not in self.__non_root_elements:
          self.__non_root_elements.add(e)
      nm_index = nm_index + 1
    return self

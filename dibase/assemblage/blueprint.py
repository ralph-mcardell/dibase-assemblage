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

import logging

class Blueprint:
  '''
  Provide blueprint plans for assemblages.
  Instances can be passed to assemblage.Assemblage constructor to create
  a set of element trees of assemblage.Components or similar to which actions
  can be applied.
  '''
  class __ElementSpec:
    def __init__(self, name, kind, elements, logger, **kwargs):
      self.name = name
      self.kind = kind
      self.elements = elements
      self.logger = logger
      self.args = kwargs

  class __ElementView:
    def __init__(self, by_group):
      self.__elements_by_group = {}
      for k,v in by_group.items():
        self.__elements_by_group[k] = []
        for es in v:
          self.__elements_by_group[k].append(es.name)
    def groups(self):
      return self.__elements_by_group.keys()
    def has_group(self, group):
      return group in self.groups()
    def elements(self, group):
      return self.__elements_by_group[group] if self.has_group(group) else []
    def has_element(self, group, element):
      return self.has_group(group) and element in self.elements(group)

  def __init__(self):
    self.__log = None
    self.__element_specs_by_group = {}
    self.__element_specs_by_name = {}
    self.__non_root_elements = set()

  def __set_default_logger(self):
    loghdr = logging.StreamHandler()
    loghdr.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    loghdr.setFormatter(formatter)
    self.__log = logging.getLogger("assemblage.default")
    self.__log.addHandler(loghdr)
    self.__log.setLevel(logging.INFO)

  def __add_element_from_specification(self, specification, elements):
    subelements = []
    for subname in specification.elements:
      if subname in elements:
        subelements.append(elements[subname])
      else: # element not created yet - go make it
        if subname in self.__element_specs_by_name:
          self.__add_element_from_specification(self.__element_specs_by_name[subname], elements)
          subelements.append(elements[subname])
        else:
          raise RuntimeError("Element undefined: No element added with name '%(e)s'" % {'e':subname})
    elements[specification.name] = \
      (specification.kind(name=specification.name,elements=subelements,logger=specification.logger,**specification.args))

  def logger(self):
    if not self.__log:
      self.__set_default_logger()
    return self.__log

  def setLogger(self, logger):
    self.__log = logger

  def topLevelElements(self):
    elements = {}
    for es in self.__element_specs_by_name.values():
      if not es.logger:
        es.logger = self.logger()
      if es.name not in elements.keys():
        self.__add_element_from_specification(es, elements)
    tlelements = []
    for ename, element in elements.items():
      if ename not in self.__non_root_elements:
        tlelements.append(element)
    return tlelements

  def addElements(self, names, kind, group='', elements=[], logger=None, **kwargs):
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
    def resolve_to_list(value):
      if type(value) is str:
        return [value]
      elif callable(value):
        return value(Blueprint.__ElementView(self.__element_specs_by_group))
      else:
        return value

    names = resolve_to_list(names)
    elements = resolve_to_list(elements)
    nm_index = 0
    for name in names:
      if name in self.__element_specs_by_name:
        raise RuntimeError("Duplicate element: there is already an element called '%(n)s'." % {'n':name})
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

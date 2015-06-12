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
          raise RuntimeError("No definition for element '%(e)s' in Blueprint." % {'e':subname})
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
    if type(elements) is str:
      elements = [elements]
    if names in self.__element_specs_by_name:
      raise RuntimeError("Duplicate element: there is already an element called '%(n)s'." % {'n':es.name})
    new_spec = Blueprint.__ElementSpec(names, kind, elements, logger, **kwargs)
    self.__element_specs_by_name[names] = new_spec
    if group not in self.__element_specs_by_group:
      self.__element_specs_by_group[group] = []
    self.__element_specs_by_group[group].append(new_spec)
    for e in elements:
      if e not in self.__non_root_elements:
        self.__non_root_elements.add(e)

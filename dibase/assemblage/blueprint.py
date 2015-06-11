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
    self.element_specs = {}

  def __set_default_logger(self):
    loghdr = logging.StreamHandler()
    loghdr.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    loghdr.setFormatter(formatter)
    self.__log = logging.getLogger("assemblage.default")
    self.__log.addHandler(loghdr)
    self.__log.setLevel(logging.INFO)

  def logger(self):
    if not self.__log:
      self.__set_default_logger()
    return self.__log

  def setLogger(self, logger):
    self.__log = logger

  def topLevelElements(self):
    elements = []
    for es in self.element_specs.values():
      if not es.logger:
        es.logger = self.logger()
      elements.append(es.kind(name=es.name,elements=es.elements,logger=es.logger,**es.args))
    return elements

  def addElements(self, names, kind, group='', elements=[], logger=None, **kwargs):
    self.element_specs[group] = Blueprint.__ElementSpec(names, kind, elements, logger, **kwargs)
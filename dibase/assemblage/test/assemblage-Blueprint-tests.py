#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.Blueprint
"""
import unittest
import logging
import io

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from blueprint import Blueprint

class TestComponent:
  def __init__(self, name, elements, logger, **kwargs):
    self.name = name
    self.elements = elements
    self.logger = logger
    self.args = kwargs
  def __lt__(self,other):
    return self.name < other.name

class TestAssemblageBlueprint(unittest.TestCase):
  def test_default_blueprint_has_usaable_default_logger(self):
    self.assertIsInstance(Blueprint().logger(), logging.Logger)
    self.assertTrue(Blueprint().logger().hasHandlers())
    self.assertTrue(Blueprint().logger().isEnabledFor(logging.INFO))
  def test_blueprint_logger_returns_specific_logger_if_one_set_with_setlogger(self):
    stringstream = io.StringIO()
    loghdr = logging.StreamHandler(stringstream)
    formatter = logging.Formatter('SETLOGGERTEST: %(levelname)s: %(message)s')
    loghdr.setFormatter(formatter)
    log = logging.getLogger('.'.join([__name__, "test_blueprint_logger_returns_specific_logger_if_one_set_with_setlogger"]))
    log.addHandler(loghdr)
    log.setLevel(logging.DEBUG)
    b = Blueprint()
    b.setLogger(log)
    self.assertTrue(b.logger().isEnabledFor(logging.DEBUG))
    b.logger().debug('Oops!')
    self.assertEqual(stringstream.getvalue(),'SETLOGGERTEST: DEBUG: Oops!\n')
  def test_blueprint_topLevelElements_returns_false_if_no_elements_added(self):
    self.assertFalse(Blueprint().topLevelElements())
  def test_blueprint_topLevelElements_returns_properly_initialised_element_if_one_added(self):
    b = Blueprint()
    b.addElements('testelement',TestComponent)
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement')
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_blueprint_topLevelElements_returns_element_with_additional_initialisation_parameters_passed_if_one_added(self):
    b = Blueprint()
    b.addElements('testelement',TestComponent, custom_arg='custom', another_arg='arg2')
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom')
      self.assertEqual(e.args['another_arg'], 'arg2')
  def test_blueprint_topLevelElements_returns_element_with_additional_specific_initialisation_parameters_passed_if_one_added(self):
    class LocalComponent:
      def __init__(self, name, elements, logger, arg1, arg2):
        self.name = name
        self.elements = elements
        self.logger = logger
        self.arg1 = arg1
        self.arg2 = arg2
    b = Blueprint()
    b.addElements('testelement',LocalComponent, arg1='custom', arg2='arg2')
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertEqual(e.arg1, 'custom')
      self.assertEqual(e.arg2, 'arg2')
  def test_blueprint_topLevelElements_returns_properly_initialised_elements_if_some_added(self):
    b = Blueprint()
    b.addElements('testelement1',TestComponent)
    b.addElements('testelement2',TestComponent)
    b.addElements('testelement3',TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_blueprint_topLevelElements_returns_elements_with_additional_initialisation_parameters_passed_if_some_added(self):
    b = Blueprint()
    b.addElements('testelement1',TestComponent, custom_arg='custom1', another_arg='arg2-1')
    b.addElements('testelement2',TestComponent, custom_arg='custom2', another_arg='arg2-2')
    b.addElements('testelement3',TestComponent, custom_arg='custom3', another_arg='arg2-3')
    tle = b.topLevelElements()
    self.assertEqual(len(tle),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom%(n)d' % {'n':n})
      self.assertEqual(e.args['another_arg'], 'arg2-%(n)d' % {'n':n})

  def test_blueprint_topLevelElements_returns_elements_with_additional_specific_initialisation_parameters_passed_if_some_added(self):
    class LocalComponent:
      def __init__(self, name, elements, logger, arg1, arg2):
        self.name = name
        self.elements = elements
        self.logger = logger
        self.arg1 = arg1
        self.arg2 = arg2
      def __lt__(self,other):
        return self.name < other.name
    b = Blueprint()
    b.addElements('testelement1',LocalComponent, arg1='custom1', arg2='arg2-1')
    b.addElements('testelement2',LocalComponent, arg1='custom2', arg2='arg2-2')
    b.addElements('testelement3',LocalComponent, arg1='custom3', arg2='arg2-3')
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertEqual(e.arg1, 'custom%(n)d' % {'n':n})
      self.assertEqual(e.arg2, 'arg2-%(n)d' % {'n':n})

  def test_blueprint_topLevelElements_returns_single_element_if_one_added_with_another_as_subelement_root_defined_last(self):
    b = Blueprint()
    b.addElements('rootDependsOn',TestComponent)
    b.addElements('root',TestComponent, elements='rootDependsOn')
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'root')
      self.assertIs(e.logger, b.logger())
      self.assertTrue(e.elements)
      self.assertEqual(len(e.elements),1)
      for sub in e.elements:
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'rootDependsOn')
        self.assertIs(sub.logger, b.logger())

  def test_blueprint_topLevelElements_returns_single_element_if_one_added_with_another_as_subelement_root_defined_first(self):
    b = Blueprint()
    b.addElements('root',TestComponent, elements='rootDependsOn')
    b.addElements('rootDependsOn',TestComponent)
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'root')
      self.assertIs(e.logger, b.logger())
      self.assertTrue(e.elements)
      self.assertEqual(len(e.elements),1)
      for sub in e.elements:
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'rootDependsOn')
        self.assertIs(sub.logger, b.logger())
        self.assertFalse(sub.elements)

#    .withLogger()
#      .addHandler()
#      .addFilter()
#    .done()
#    .addElements(names,kind,group='', elements=None)

if __name__ == '__main__':
  unittest.main()
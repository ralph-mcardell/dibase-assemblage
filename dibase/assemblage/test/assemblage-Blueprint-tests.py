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

#    .withLogger()
#      .addHandler()
#      .addFilter()
#    .done()
#    .addElements(names,kind,group='', elements=None)
    
    
    
if __name__ == '__main__':
  unittest.main()

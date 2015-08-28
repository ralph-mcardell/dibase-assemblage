#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.logging.configureLogger et al tests 
"""
import unittest

import os,sys
project_root_dir = os.path.dirname(
                    os.path.dirname(
                      os.path.dirname(
                        os.path.dirname( os.path.realpath(__file__)
                        )    # this directory 
                      )      # assemblage directory 
                    )        # dibase directory 
                  )          # project directory
if project_root_dir not in sys.path:
  sys.path.insert(0, project_root_dir)
from dibase.assemblage.logging import Allow
from dibase.assemblage.logging import Deny
from dibase.assemblage.logging import configureLogger
from dibase.assemblage.logging import addHandler
from dibase.assemblage.logging import specifyLoggedLevels
from dibase.assemblage.logging import logLevelsFor

class Record:
  def __init__(self, level, args=[]):
    self.level = level
    self.args = args

class Handler:
  def __init__(self):
    self.formatter = None
    self.filters = []
  def setFormatter(self,fmtr):
    self.formatter = fmtr
  def addFilter(self,filt):
    self.filters.append(filt)
class TestLogger:
  def __init__(self):
    self.handlers = []
    self.filters = []
  def addHandler(self, hdlr):
    self.handlers.append(hdlr)
  def addFilter(self,filt):
    self.filters.append(filt)

test_logger = None

class TestAssemblageLoggingConfiguration(unittest.TestCase):
  def test_configuring_a_logger_with_specified_logged_level_for_one_object(self):
    global test_logger
    test_logger = TestLogger()
    o = 'value_of_o'
    allowedLevel = 111
    configureLogger(
      specifyLoggedLevels(
        logLevelsFor( o
        , Allow(lambda lvl:lvl==allowedLevel)
        )
      )
    , logger=test_logger
    )
    self.assertEqual(len(test_logger.handlers),0)
    self.assertEqual(len(test_logger.filters),1)
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel-1,o)))
    self.assertTrue(test_logger.filters[0].filter(Record(allowedLevel,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel+1,o)))
    self.assertTrue(test_logger.filters[0].filter(Record(allowedLevel,'value_of_o')))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel+1,'value_of_o')))
  def test_configuring_a_logger_with_specified_logged_levels_for_one_object(self):
    global test_logger
    test_logger = TestLogger()
    o = 'value_of_o'
    allowedLevel = 123
    configureLogger(
      specifyLoggedLevels(
        logLevelsFor( o
        , Allow(lambda lvl:lvl==allowedLevel)
        , Allow(lambda lvl:lvl==2*allowedLevel)
        )
      )
    , logger=test_logger
    )
    self.assertEqual(len(test_logger.handlers),0)
    self.assertEqual(len(test_logger.filters),1)
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel-1,o)))
    self.assertTrue(test_logger.filters[0].filter(Record(allowedLevel,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel+1,o)))
    self.assertTrue(test_logger.filters[0].filter(Record(allowedLevel,'value_of_o')))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel+1,'value_of_o')))
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel-1,o)))
    self.assertTrue(test_logger.filters[0].filter(Record(2*allowedLevel,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel+1,o)))
  def test_configuring_a_logger_with_specified_logged_level_for_multiple_entities(self):
    global test_logger
    test_logger = TestLogger()
    class TestType:
      pass
    o = 'value_of_o'
    allowedLevel = 31
    configureLogger(
      specifyLoggedLevels(
        logLevelsFor( o
        , Allow(lambda lvl:lvl==allowedLevel)
        )
      , logLevelsFor( TestType
        , Allow(lambda lvl:lvl==2*allowedLevel)
        )
      , logLevelsFor( None
        , Allow(lambda lvl:lvl==3*allowedLevel)
        )
      )
    , logger=test_logger
    )
    self.assertEqual(len(test_logger.handlers),0)
    self.assertEqual(len(test_logger.filters),1)
    
    tt = TestType()
    o2 = 'another string value'
    # Only object o gets to log to allowedLevel
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel-1,o)))
    self.assertTrue(test_logger.filters[0].filter(Record(allowedLevel,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel+1,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel,o2)))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel,tt)))
    self.assertFalse(test_logger.filters[0].filter(Record(allowedLevel,allowedLevel)))

    # Only objects of type TestType o gets to log to 2*allowedLevel
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel-1,tt)))
    self.assertTrue(test_logger.filters[0].filter(Record(2*allowedLevel,tt)))
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel+1,tt)))
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel,o2)))
    self.assertFalse(test_logger.filters[0].filter(Record(2*allowedLevel,allowedLevel)))

    # All objects not object o or of type TestType get to log to 3*allowedLevel
    self.assertFalse(test_logger.filters[0].filter(Record(3*allowedLevel-1,allowedLevel)))
    self.assertTrue(test_logger.filters[0].filter(Record(3*allowedLevel,allowedLevel)))
    self.assertFalse(test_logger.filters[0].filter(Record(3*allowedLevel+1,allowedLevel)))
    self.assertFalse(test_logger.filters[0].filter(Record(3*allowedLevel-1,o2)))
    self.assertTrue(test_logger.filters[0].filter(Record(3*allowedLevel,o2)))
    self.assertFalse(test_logger.filters[0].filter(Record(3*allowedLevel+1,o2)))
    self.assertFalse(test_logger.filters[0].filter(Record(3*allowedLevel,o)))
    self.assertFalse(test_logger.filters[0].filter(Record(3*allowedLevel,tt)))
  def test_configuring_a_logger_with_single_handler_with_specified_logged_level_for_one_object(self):
    global test_logger
    test_logger = TestLogger()
    o = 'value_of_o'
    allowedLevel = 102
    configureLogger(
      addHandler( Handler()
      , specifyLoggedLevels(
          logLevelsFor( o
          , Allow(lambda lvl:lvl==allowedLevel)
          )
        )
      )
    , logger=test_logger
    )
    self.assertEqual(len(test_logger.handlers),1)
    self.assertIsInstance(test_logger.handlers[0],Handler)
    self.assertEqual(len(test_logger.handlers[0].filters),1)
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel-1,o)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,o)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel+1,o)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,'value_of_o')))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel+1,'value_of_o')))
  def test_configuring_a_logger_with_single_handler_with_specified_logged_level_for_for_multiple_entities(self):
    global test_logger
    test_logger = TestLogger()
    class TestType:
      pass
    o = 'value_of_o'
    allowedLevel = 633
    configureLogger(
      addHandler( Handler()
      , specifyLoggedLevels(
          logLevelsFor( o
          , Allow(lambda lvl:lvl==allowedLevel)
          )
        , logLevelsFor( TestType
          , Allow(lambda lvl:lvl==2*allowedLevel)
          )
        , logLevelsFor( None
          , Allow(lambda lvl:lvl==3*allowedLevel)
          )
        )
      )
    , logger=test_logger
    )
    tt = TestType()
    o2 = 'another string value'
    # Only object o gets to log to allowedLevel
    self.assertEqual(len(test_logger.handlers),1)
    self.assertIsInstance(test_logger.handlers[0],Handler)
    self.assertEqual(len(test_logger.handlers[0].filters),1)
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel-1,o)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,o)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel+1,o)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,o2)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,tt)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,allowedLevel)))

    # Only objects of type TestType o gets to log to 2*allowedLevel
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(2*allowedLevel-1,tt)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(2*allowedLevel,tt)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(2*allowedLevel+1,tt)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(2*allowedLevel,o)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(2*allowedLevel,o2)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(2*allowedLevel,allowedLevel)))

    # All objects not object o or of type TestType get to log to 3*allowedLevel
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel-1,allowedLevel)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel,allowedLevel)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel+1,allowedLevel)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel-1,o2)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel,o2)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel+1,o2)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel,o)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(3*allowedLevel,tt)))
  def test_configuring_a_logger_with_multiple_handlers_with_specified_logged_level_for_one_object(self):
    global test_logger
    test_logger = TestLogger()
    o = 'value_of_o'
    allowedLevel = 55
    configureLogger(
      addHandler( Handler()
      , specifyLoggedLevels(
          logLevelsFor( o
          , Allow(lambda lvl:lvl==allowedLevel)
          )
        )
      )
    , addHandler( Handler()
      , specifyLoggedLevels(
          logLevelsFor( o
          , Allow(lambda lvl:lvl==2*allowedLevel)
          )
        )
      )
    , logger=test_logger
    )
    self.assertEqual(len(test_logger.handlers),2)
    self.assertIsInstance(test_logger.handlers[0],Handler)
    self.assertEqual(len(test_logger.handlers[0].filters),1)
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel-1,o)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,o)))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel+1,o)))
    self.assertTrue(test_logger.handlers[0].filters[0].filter(Record(allowedLevel,'value_of_o')))
    self.assertFalse(test_logger.handlers[0].filters[0].filter(Record(allowedLevel+1,'value_of_o')))

    self.assertIsInstance(test_logger.handlers[1],Handler)
    self.assertEqual(len(test_logger.handlers[1].filters),1)
    self.assertFalse(test_logger.handlers[1].filters[0].filter(Record(2*allowedLevel-1,o)))
    self.assertTrue(test_logger.handlers[1].filters[0].filter(Record(2*allowedLevel,o)))
    self.assertFalse(test_logger.handlers[1].filters[0].filter(Record(allowedLevel+1,o)))
    self.assertTrue(test_logger.handlers[1].filters[0].filter(Record(2*allowedLevel,'value_of_o')))
    self.assertFalse(test_logger.handlers[1].filters[0].filter(Record(2*allowedLevel+1,'value_of_o')))
    
if __name__ == '__main__':
  unittest.main()

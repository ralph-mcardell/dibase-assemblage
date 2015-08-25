#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.logging.Level tests 
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
from dibase.assemblage.logging import Level

class TestAssemblageLoggingLevel(unittest.TestCase):
  currentLevel = 1000
  @classmethod
  def expectedAutoLevel(cls):
    expected = cls.currentLevel 
    cls.currentLevel = expected + 1
    return expected

  def test_create_level_with_specific_arguments_reflects_creation_arguments(self):
    l = Level("TEST", "attrTest", 3)    
    self.assertEqual(l,3)
    self.assertEqual(l.name(),"TEST")
    self.assertEqual(l.attrName(),"attrTest")
  def test_create_two_levels_with_defaults_has_expected_generated_values(self):
    l1 = Level("UNIT")    
    l2 = Level("TEST")    
    self.assertEqual(l1,self.expectedAutoLevel())
    self.assertEqual(l1.name(),"UNIT")
    self.assertEqual(l1.attrName(),"unit")
    self.assertEqual(l2,self.expectedAutoLevel())
    self.assertEqual(l2.name(),"TEST")
    self.assertEqual(l2.attrName(),"test")
  def test_bad_create_level_raises_ValueError_for_keyword_attrName(self):
    with self.assertRaises(ValueError):
      l = Level("TEST", "class", 4)    
    with self.assertRaises(ValueError):
      l = Level("CLASS")    
  def test_bad_create_level_raises_ValueError_for_bad_identifer_attrName(self):
    with self.assertRaises(ValueError):
      l = Level("TEST", "1234", 13)    
    with self.assertRaises(ValueError):
      l = Level("1TEST")    
  def test_bad_create_level_raises_TypeError_for_non_string_name(self):
    with self.assertRaises(TypeError):
      l = Level(1234, "test", 14)    
    with self.assertRaises(TypeError):
      l = Level(44.4)    
  def test_bad_create_level_raises_ValueError_for_non_int_value(self):
    with self.assertRaises(TypeError):
      l = Level("BADTEST", value="1234")    
    with self.assertRaises(TypeError):
      l = Level("BADTEST", value=55.4)    
  def test_bad_create_level_raises_ValueError_for_negative_value(self):
    with self.assertRaises(ValueError):
      l = Level("TEST", "class", -4)    
    with self.assertRaises(ValueError):
      l = Level("CLASS", value=-1)    
    
if __name__ == '__main__':
  unittest.main()

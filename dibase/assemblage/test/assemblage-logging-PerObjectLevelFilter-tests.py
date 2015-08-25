#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.logging.PerObjectLevelFilter tests 
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
from dibase.assemblage.logging import PerObjectLevelFilter
from dibase.assemblage.logging import Allow
from dibase.assemblage.logging import Deny

class Record:
  def __init__(self, level, args=[]):
    self.level = level
    self.args = args

class TestAssemblageLoggingPerObjectLevelFilter(unittest.TestCase):
  def test_create_empty_denys_all_levels(self):
    f = PerObjectLevelFilter()
    self.assertFalse(f.filter(Record(0)))
    self.assertFalse(f.filter(Record(10)))
    self.assertFalse(f.filter(Record(20)))
    self.assertFalse(f.filter(Record(50)))
    self.assertFalse(f.filter(Record(100)))
    self.assertFalse(f.filter(Record(1000)))
  def test_create_with_none_denys_all_levels(self):
    f = PerObjectLevelFilter(None)
    self.assertFalse(f.filter(Record(0)))
    self.assertFalse(f.filter(Record(10)))
    self.assertFalse(f.filter(Record(20)))
    self.assertFalse(f.filter(Record(50)))
    self.assertFalse(f.filter(Record(100)))
    self.assertFalse(f.filter(Record(1000)))
  def test_create_with_multiple_none_denys_all_levels(self):
    f = PerObjectLevelFilter(None,None,None)
    self.assertFalse(f.filter(Record(0)))
    self.assertFalse(f.filter(Record(10)))
    self.assertFalse(f.filter(Record(20)))
    self.assertFalse(f.filter(Record(50)))
    self.assertFalse(f.filter(Record(100)))
    self.assertFalse(f.filter(Record(1000)))
  def test_create_empty_denys_all_levels_for_all_objects(self):
    o1 = 'o1'
    o2 = 2
    o3 = 3.01
    f = PerObjectLevelFilter({o1 : None, o2 : [None], o3: (None,None)})
    self.assertFalse(f.filter(Record(0,o1)))
    self.assertFalse(f.filter(Record(10,o2)))
    self.assertFalse(f.filter(Record(20,o3)))
    self.assertFalse(f.filter(Record(50,{'object':o1})))
    self.assertFalse(f.filter(Record(100,[{'object':o2}])))
    self.assertFalse(f.filter(Record(1000,args=({'object':o3}))))
  def test_create_empty_denys_all_levels_for_all_objects_of_type(self):
    class TheType:
      pass
    o1 = TheType()
    o2 = TheType()
    o3 = TheType()
    f = PerObjectLevelFilter({TheType : None})
    self.assertFalse(f.filter(Record(0,o1)))
    self.assertFalse(f.filter(Record(10,o2)))
    self.assertFalse(f.filter(Record(20,o3)))
    self.assertFalse(f.filter(Record(50,{'object':o1})))
    self.assertFalse(f.filter(Record(100,[{'object':o2}])))
    self.assertFalse(f.filter(Record(1000,args=({'object':o3}))))
  def test_create_with_allow_any_allows_all_levels(self):
    f = PerObjectLevelFilter(Allow(lambda l: True))
    self.assertTrue(f.filter(Record(0)))
    self.assertTrue(f.filter(Record(10)))
    self.assertTrue(f.filter(Record(20)))
    self.assertTrue(f.filter(Record(50)))
    self.assertTrue(f.filter(Record(100)))
    self.assertTrue(f.filter(Record(1000)))
  def test_create_with_multiple_with_allow_any_allows_all_levels(self):
    f = PerObjectLevelFilter(Allow(lambda l: l<30),Allow(lambda l: l==30),Allow(lambda l: l>30) )
    self.assertTrue(f.filter(Record(0)))
    self.assertTrue(f.filter(Record(10)))
    self.assertTrue(f.filter(Record(20)))
    self.assertTrue(f.filter(Record(50)))
    self.assertTrue(f.filter(Record(100)))
    self.assertTrue(f.filter(Record(1000)))
  def test_create_with_allow_any_allows_level_for_all_objects(self):
    o1 = 'o1'
    o2 = 2
    o3 = 3.01
    f = PerObjectLevelFilter( { o1 : Allow(lambda l: True)
                              , o2 :[Allow(lambda l: l<30),Allow(lambda l: l==30),Allow(lambda l: l>30)]
                              , o3 :(Allow(lambda l: True))
                              }
                            )
    self.assertTrue(f.filter(Record(0,o1)))
    self.assertTrue(f.filter(Record(10,o2)))
    self.assertTrue(f.filter(Record(20,o3)))
    self.assertTrue(f.filter(Record(50,{'object':o1})))
    self.assertTrue(f.filter(Record(100,[{'object':o2}])))
    self.assertTrue(f.filter(Record(1000,args=({'object':o3}))))
  def test_create_with_allow_any_allows_levels_for_all_objects_of_type(self):
    class TheType:
      pass
    o1 = TheType()
    o2 = TheType()
    o3 = TheType()
    f = PerObjectLevelFilter({TheType:[Allow(lambda l: l<30),Allow(lambda l: l==30),Allow(lambda l: l>30)]})
    self.assertTrue(f.filter(Record(0,o1)))
    self.assertTrue(f.filter(Record(10,o2)))
    self.assertTrue(f.filter(Record(20,o3)))
    self.assertTrue(f.filter(Record(50,{'object':o1})))
    self.assertTrue(f.filter(Record(100,[{'object':o2}])))
    self.assertTrue(f.filter(Record(1000,args=({'object':o3}))))
  def test_create_with_allow_some_only_allows_expected_levels_(self):
    f = PerObjectLevelFilter(Allow(lambda l: l<50))
    self.assertTrue(f.filter(Record(0)))
    self.assertTrue(f.filter(Record(10)))
    self.assertTrue(f.filter(Record(20)))
    self.assertFalse(f.filter(Record(50)))
    self.assertFalse(f.filter(Record(100)))
    self.assertFalse(f.filter(Record(1000)))
  def test_create_with_allow_some_allows_expected_levels_for_each_object(self):
    o1 = 'o1'
    o2 = 2
    o3 = 3.01
    f = PerObjectLevelFilter( { o1 : Allow(lambda l: l<20)
                              , o2 :[Allow(lambda l: l>50),Allow(lambda l: l<20)]
                              , o3 :(Allow(lambda l: l==10))
                              }
                            )
    self.assertTrue(f.filter(Record(0,o1)))
    self.assertTrue(f.filter(Record(19,o1)))
    self.assertFalse(f.filter(Record(20,o1)))
    self.assertTrue(f.filter(Record(51,[{'object':o2}])))
    self.assertTrue(f.filter(Record(19,o2)))
    self.assertFalse(f.filter(Record(20,o2)))
    self.assertFalse(f.filter(Record(50,o2)))
    self.assertFalse(f.filter(Record(9,o3)))
    self.assertTrue(f.filter(Record(10,o3)))
    self.assertFalse(f.filter(Record(11,o3)))
  def test_create_with_allow_some_allows_expected_levels_for_each_object_of_type(self):
    class TheType:
      pass
    o1 = TheType()
    o2 = TheType()
    o3 = TheType()
    f = PerObjectLevelFilter({TheType : [Allow(lambda l: l>50),Allow(lambda l: l<20)]})
    self.assertTrue(f.filter(Record(51,[{'object':o1}])))
    self.assertTrue(f.filter(Record(19,o1)))
    self.assertFalse(f.filter(Record(20,o1)))
    self.assertFalse(f.filter(Record(50,o1)))
    self.assertTrue(f.filter(Record(51,[{'object':o2}])))
    self.assertTrue(f.filter(Record(19,o2)))
    self.assertFalse(f.filter(Record(20,o2)))
    self.assertFalse(f.filter(Record(50,o2)))
    self.assertTrue(f.filter(Record(51,[{'object':o3}])))
    self.assertTrue(f.filter(Record(19,o3)))
    self.assertFalse(f.filter(Record(20,o3)))
    self.assertFalse(f.filter(Record(50,o3)))
  def test_create_with_mixed_allow_deny_ranges_only_allows_expected_levels(self):
    f = PerObjectLevelFilter(Allow(lambda l:l>=20),Deny(lambda l:l>50),Allow(lambda l:l==1000))
    self.assertFalse(f.filter(Record(0)))
    self.assertFalse(f.filter(Record(19)))
    self.assertTrue(f.filter(Record(20)))
    self.assertTrue(f.filter(Record(50)))
    self.assertFalse(f.filter(Record(51)))
    self.assertFalse(f.filter(Record(999)))
    self.assertTrue(f.filter(Record(1000)))
    self.assertFalse(f.filter(Record(1001)))
  def test_create_with_mixed_allow_deny_ranges_only_allows_expected_levels_for_each_object(self):
    o1 = 'o1'
    o2 = 2
    o3 = 3.01
    f = PerObjectLevelFilter( { o1 : [Allow(lambda l: l<=50), Deny(lambda l:l==1)]
                              , o2 :[Allow(lambda l:l>=20),Deny(lambda l:l>50),Allow(lambda l:l==1000)]
                              , o3 :(Allow(lambda l: l<=50), Deny(lambda l:l<20))
                              }
                            )
    self.assertTrue(f.filter(Record(0,o1)))
    self.assertTrue(f.filter(Record(50,o1)))
    self.assertFalse(f.filter(Record(51,o1)))
    self.assertFalse(f.filter(Record(1,o1)))
    self.assertTrue(f.filter(Record(20,[{'object':o2}])))
    self.assertTrue(f.filter(Record(50,o2)))
    self.assertTrue(f.filter(Record(1000,o2)))
    self.assertFalse(f.filter(Record(0,o2)))
    self.assertFalse(f.filter(Record(19,o2)))
    self.assertFalse(f.filter(Record(51,o2)))
    self.assertFalse(f.filter(Record(999,o2)))
    self.assertFalse(f.filter(Record(1001,o2)))
    self.assertFalse(f.filter(Record(51,o3)))
    self.assertTrue(f.filter(Record(50,o3)))
    self.assertTrue(f.filter(Record(20,o3)))
    self.assertFalse(f.filter(Record(19,o3)))
  def test_create_with_mixed_allow_deny_ranges_only_allows_expected_levels_for_each_object_of_type(self):
    class TheType:
      pass
    o1 = TheType()
    o2 = TheType()
    o3 = TheType()
    f = PerObjectLevelFilter({TheType : [Allow(lambda l:l>=20),Deny(lambda l:l>50),Allow(lambda l:l==1000)]})
    self.assertTrue(f.filter(Record(20,[{'object':o1}])))
    self.assertTrue(f.filter(Record(50,o1)))
    self.assertTrue(f.filter(Record(1000,o1)))
    self.assertFalse(f.filter(Record(0,o1)))
    self.assertFalse(f.filter(Record(19,o1)))
    self.assertFalse(f.filter(Record(51,o1)))
    self.assertFalse(f.filter(Record(999,o1)))
    self.assertFalse(f.filter(Record(1001,o1)))
    self.assertTrue(f.filter(Record(20,[{'object':o2}])))
    self.assertTrue(f.filter(Record(50,o2)))
    self.assertTrue(f.filter(Record(1000,o2)))
    self.assertFalse(f.filter(Record(0,o2)))
    self.assertFalse(f.filter(Record(19,o2)))
    self.assertFalse(f.filter(Record(51,o2)))
    self.assertFalse(f.filter(Record(999,o2)))
    self.assertFalse(f.filter(Record(1001,o2)))
    self.assertTrue(f.filter(Record(20,[{'object':o3}])))
    self.assertTrue(f.filter(Record(50,o3)))
    self.assertTrue(f.filter(Record(1000,o3)))
    self.assertFalse(f.filter(Record(0,o3)))
    self.assertFalse(f.filter(Record(19,o3)))
    self.assertFalse(f.filter(Record(51,o3)))
    self.assertFalse(f.filter(Record(999,o3)))
    self.assertFalse(f.filter(Record(1001,o3)))
  def test_filter_applies_filtering_on_object_then_type_then_None(self):
    class TheType:
      pass
    o1 = TheType()
    o2 = TheType()
    o3 = 'O3'

    f = PerObjectLevelFilter( { o1      : Allow(lambda l: l==10)
                              , TheType : Allow(lambda l: l==30)
                              , None    : Allow(lambda l: l==50)
                              }
                            )
    self.assertFalse(f.filter(Record(9,o1)))
    self.assertTrue(f.filter(Record(10,o1)))
    self.assertFalse(f.filter(Record(11,o1)))
    self.assertFalse(f.filter(Record(29,o2)))
    self.assertTrue(f.filter(Record(30,o2)))
    self.assertFalse(f.filter(Record(31,o2)))
    self.assertFalse(f.filter(Record(49,o3)))
    self.assertTrue(f.filter(Record(50,o3)))
    self.assertFalse(f.filter(Record(51,o3)))
  def test_raises_ValueError_on_create_if_first_argument_dict_with_many_arguments(self):
    with self.assertRaises(ValueError):
      f = PerObjectLevelFilter({},None)
  def test_raises_ValueError_on_create_if_argument_not_None_Allow_or_Deny(self):
    with self.assertRaises(ValueError):
      f = PerObjectLevelFilter(None, {})

if __name__ == '__main__':
  unittest.main()

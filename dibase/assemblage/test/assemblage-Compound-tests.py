#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.compound.Compound 
"""
import unittest
import io
import logging
import inspect

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
from dibase.assemblage.compound import Compound
from dibase.assemblage.interfaces import ComponentBase

testAttributes = {}

class TestComponent(ComponentBase):
  def __init__(self):
    self.doAfter = False
    self.doBefore = False
    self.beforeDone = False
    self.afterDone = False
  def queryBeforeElementsActionsDone(self):
    return self.beforeDone
  def queryAfterElementsActionsDone(self):
    return self.afterDone
  def digest(self):
    pass
  def doesNotExist(self):
    pass
  def hasChanged(self):
    pass
  def isOutOfDate(self):
    pass
  def __str__(self):
    return "TestComponent"
#  def elementAttribute(self, id, name, default=AttributeError):
#    pass
  def apply(self, action):
    pass
  def _applyInner(self, action, scope):
    self.beforeDone = self.doBefore
    self.afterDone = self.doAfter

class TestAssemblageCompound(unittest.TestCase):
    def test_newly_contructed_Compound_has_every_action_Done_state_False(self):
      c = Compound(testAttributes)
      self.assertFalse(c.queryAnyBeforeElementsActionsDone())
      self.assertFalse(c.queryAllBeforeElementsActionsDone())
      self.assertFalse(c.queryAnyAfterElementsActionsDone())
      self.assertFalse(c.queryAllAfterElementsActionsDone())
    def test_apply_to_Compound_with_no_elements_has_AnyXXXActions_states_False_and_AllXXXActions_states_True(self):
      c = Compound(testAttributes)
      c.apply('NonexistentAction')
      self.assertFalse(c.queryAnyBeforeElementsActionsDone())
      self.assertTrue(c.queryAllBeforeElementsActionsDone())
      self.assertFalse(c.queryAnyAfterElementsActionsDone())
      self.assertTrue(c.queryAllAfterElementsActionsDone())
    def test_apply_to_Compound_with_one_element_has_AnyXXXActions_and_AllXXXActions_states_in_same_state(self):
      tc = TestComponent()
      c = Compound(testAttributes, [tc])
      c.apply('NonexistentAction')
      self.assertFalse(c.queryAnyBeforeElementsActionsDone())
      self.assertFalse(c.queryAllBeforeElementsActionsDone())
      self.assertFalse(c.queryAnyAfterElementsActionsDone())
      self.assertFalse(c.queryAllAfterElementsActionsDone())
      tc.doBefore = True
      tc.doAfter = True
      c.apply('NonexistentAction')
      self.assertTrue(c.queryAnyBeforeElementsActionsDone())
      self.assertTrue(c.queryAllBeforeElementsActionsDone())
      self.assertTrue(c.queryAnyAfterElementsActionsDone())
      self.assertTrue(c.queryAllAfterElementsActionsDone())
    def test_apply_to_Compound_with_multiple_elements_has_AnyXXXActions_and_AllXXXActions_in_expected_states(self):
      tc1 = TestComponent()
      tc2 = TestComponent()
      c = Compound(testAttributes, [tc1,tc2])
      c.apply('NonexistentAction')
      self.assertFalse(c.queryAnyBeforeElementsActionsDone())
      self.assertFalse(c.queryAllBeforeElementsActionsDone())
      self.assertFalse(c.queryAnyAfterElementsActionsDone())
      self.assertFalse(c.queryAllAfterElementsActionsDone())
      tc1.doBefore = True
      tc1.doAfter = True
      c.apply('NonexistentAction')
      self.assertTrue(c.queryAnyBeforeElementsActionsDone())
      self.assertFalse(c.queryAllBeforeElementsActionsDone())
      self.assertTrue(c.queryAnyAfterElementsActionsDone())
      self.assertFalse(c.queryAllAfterElementsActionsDone())
      tc2.doBefore = True
      tc2.doAfter = True
      c.apply('NonexistentAction')
      self.assertTrue(c.queryAnyBeforeElementsActionsDone())
      self.assertTrue(c.queryAllBeforeElementsActionsDone())
      self.assertTrue(c.queryAnyAfterElementsActionsDone())
      self.assertTrue(c.queryAllAfterElementsActionsDone())
    def test_apply_to_Compound_AAABeforeXXXActions_states_independent_of_AAAAfterXXXActions_states(self):
      tc = TestComponent()
      c = Compound(testAttributes, [tc])
      tc.doBefore = True
      c.apply('NonexistentAction')
      self.assertTrue(c.queryAnyBeforeElementsActionsDone())
      self.assertTrue(c.queryAllBeforeElementsActionsDone())
      self.assertFalse(c.queryAnyAfterElementsActionsDone())
      self.assertFalse(c.queryAllAfterElementsActionsDone())
      tc.doBefore = False
      tc.doAfter = True
      c.apply('NonexistentAction')
      self.assertFalse(c.queryAnyBeforeElementsActionsDone())
      self.assertFalse(c.queryAllBeforeElementsActionsDone())
      self.assertTrue(c.queryAnyAfterElementsActionsDone())
      self.assertTrue(c.queryAllAfterElementsActionsDone())

if __name__ == '__main__':
  unittest.main()

#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.Assemblage
"""
import unittest
import logging
import io

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
from dibase.assemblage.assemblage import Assemblage
from dibase.assemblage.interfaces import AssemblagePlanBase,DigestCacheBase

class Component:
  def _applyInner(self, action):
    pass
  def apply(self, action):
    pass

class NoteApplyCalls:
  def __init__(self):
    self.applyCount = 0
  def _applyInner(self, action):
    self.applyCount = self.applyCount + 1

class NoteLastAppliedAction:
  def __init__(self):
    self.lastAction = ''
  def _applyInner(self, action):
    self.lastAction = action

class NotApplicable:
  pass

class DigestCache(DigestCacheBase):
  def updateIfDifferent(self, element):
    pass
  def writeBack(self):
    pass

class Blueprint(AssemblagePlanBase): # 'mock' Blueprint type
  def __init__(self, components=[]):
    self.components = components
    self.stringstream = io.StringIO()
    loghdr = logging.StreamHandler(self.stringstream)
    loghdr.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    loghdr.setFormatter(formatter)
    self._log = logging.getLogger('.'.join([__name__, "assemblage_Assemblage_tests.Blueprint"]))
    self._log.addHandler(loghdr)
    self._digestCache = DigestCache()
    self._attributes = {'__logger__' : self._log, '__store__' : self._digestCache}
  def logger(self):
    return self._log
  def digestCache(self):
    return self._digestCache
  def attributes(self):
    return self._attributes
  def logContents(self):
    return self.stringstream.getvalue()
  def topLevelElements(self):
    return self.components

class TestAssemblageAssemblage(unittest.TestCase):
  def test_apply_action_to_Assemblage_from_empty_blueprint_logs_warning_message(self):
    b = Blueprint()
    with self.assertLogs(b.logger(), logging.WARNING):
      Assemblage(b).apply("someAction")
    Assemblage(b).apply("yetAnotherAction")    
    self.assertEqual(b.logContents().count('\n'),1)
    print("test_apply_action_to_Assemblage_from_empty_blueprint_logs_informational_message"
            "\n  INFORMATION: Logged message: '", b.logContents()
          , "'", sep='')
  def test_apply_action_to_Assemblage_from_non_empty_blueprint_logs_no_warning_message(self):
    b = Blueprint([Component()])
    Assemblage(b).apply("anAction")    
    self.assertFalse(b.logContents())

  def test_apply_action_to_Assemblage_from_non_empty_blueprint_calls_apply_on_all_top_level_components(self):
    b = Blueprint([NoteApplyCalls(), NoteApplyCalls(), NoteApplyCalls(), NoteApplyCalls()])
    a1 = Assemblage(b)
    for c in b.topLevelElements():
      self.assertEqual(c.applyCount,0)
    a1.apply("anAction")    
    for c in b.topLevelElements():
      self.assertEqual(c.applyCount,1)
    a1.apply("anAction")    
    for c in b.topLevelElements():
      self.assertEqual(c.applyCount,2)
  def test_apply_action_to_Assemblage_from_non_empty_blueprint_applies_action_to_all_top_level_components(self):
    b = Blueprint([NoteLastAppliedAction(), NoteLastAppliedAction(), NoteLastAppliedAction(), NoteLastAppliedAction()])
    a1 = Assemblage(b)
    for c in b.topLevelElements():
      self.assertEqual(c.lastAction,'')
    a1.apply("anAction")    
    for c in b.topLevelElements():
      self.assertEqual(c.lastAction,'anAction')
    a1.apply("anotherAction")    
    for c in b.topLevelElements():
      self.assertEqual(c.lastAction,"anotherAction")
  def test_apply_action_to_Assemblage_from_non_empty_blueprint_applies_action_to_single_top_level_component(self):
    b = Blueprint(NoteLastAppliedAction())   
    a1 = Assemblage(b)
    self.assertEqual(b.topLevelElements().lastAction,'')
    a1.apply("Action_a")    
    self.assertEqual(b.topLevelElements().lastAction,'Action_a')
    a1.apply("JustDoIt")    
    self.assertEqual(b.topLevelElements().lastAction,"JustDoIt")
  def test_apply_action_to_Assemblage_from_blueprint_with_single_top_level_component_lacking_apply_method_logs_warning(self):
    b = Blueprint(NotApplicable())   
    with self.assertLogs(b.logger(), logging.WARNING):
      Assemblage(b).apply("JustDoIt")    
    Assemblage(b).apply("JustDoIt")    
    self.assertEqual(b.logContents().count('\n'),1)
    print("test_apply_action_to_Assemblage_from_blueprint_with_single_top_level_component_lacking_apply_method_logs_warning"
            "\n  INFORMATION: Logged message:\n    '", b.logContents()
          , "'", sep='')
  def test_apply_action_to_Assemblage_from_blueprint_with_many_top_level_components_lacking_apply_method_logs_warning(self):
    b = Blueprint([NotApplicable(), NotApplicable(), NotApplicable(), NotApplicable()])   
    with self.assertLogs(b.logger(), logging.WARNING):
      Assemblage(b).apply("JustDoIt")    
    Assemblage(b).apply("JustDoIt")    
    self.assertEqual(b.logContents().count('\n'),4)
  def test_Assemblage_can_be_nested_as_element_of_another_Assemblage_and_applied_actions_are_passed_through(self):
    binner = Blueprint([NoteLastAppliedAction(), NoteLastAppliedAction(), NoteLastAppliedAction(), NoteLastAppliedAction()])
    ai = Assemblage(binner)
    for c in binner.topLevelElements():
      self.assertEqual(c.lastAction,'')
    bouter = Blueprint(ai)
    ao = Assemblage(bouter)
    for c in binner.topLevelElements():
      self.assertEqual(c.lastAction,'')
    ao.apply("anAction")    
    for c in binner.topLevelElements():
      self.assertEqual(c.lastAction,'anAction')
    ao.apply("anotherAction")    
    for c in binner.topLevelElements():
      self.assertEqual(c.lastAction,"anotherAction")
  def test_can_call_logger_method_ok(self):
    self.assertIsInstance(Assemblage(Blueprint([Component()])).logger(), logging.Logger)
  def test_can_call_digestCache_method_ok(self):
    self.assertIsInstance(Assemblage(Blueprint([Component()])).digestCache(), DigestCache)

if __name__ == '__main__':
  unittest.main()

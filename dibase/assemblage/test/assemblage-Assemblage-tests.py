#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.Assemblage
"""
import unittest
import logging
import io

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from assemblage import Assemblage

class Component:
  def apply(self, action):
    pass

class NoteApplyCalls:
  def __init__(self):
    self.applyCount = 0
  def apply(self, action):
    self.applyCount = self.applyCount + 1

class NoteLastAppliedAction:
  def __init__(self):
    self.lastAction = ''
  def apply(self, action):
    self.lastAction = action

class NotApplicable:
  pass

class Blueprint: # 'mock' Blueprint type
  def __init__(self, components=[]):
    self.components = components
    self.stringstream = io.StringIO()
    loghdr = logging.StreamHandler(self.stringstream)
    loghdr.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    loghdr.setFormatter(formatter)
    self._log = logging.getLogger('.'.join([__name__, "test_apply_action_to_Assemblage_from_empty_blueprint_logs_informational_message"]))
    self._log.addHandler(loghdr)
  def logger(self):
    return self._log
  def logContents(self):
    return self.stringstream.getvalue()
  def topLevelComponents(self):
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
    for c in b.topLevelComponents():
      self.assertEqual(c.applyCount,0)
    Assemblage(b).apply("anAction")    
    for c in b.topLevelComponents():
      self.assertEqual(c.applyCount,1)
    Assemblage(b).apply("anAction")    
    for c in b.topLevelComponents():
      self.assertEqual(c.applyCount,2)
  def test_apply_action_to_Assemblage_from_non_empty_blueprint_applies_action_to_all_top_level_components(self):
    b = Blueprint([NoteLastAppliedAction(), NoteLastAppliedAction(), NoteLastAppliedAction(), NoteLastAppliedAction()])
    for c in b.topLevelComponents():
      self.assertEqual(c.lastAction,'')
    Assemblage(b).apply("anAction")    
    for c in b.topLevelComponents():
      self.assertEqual(c.lastAction,'anAction')
    Assemblage(b).apply("anotherAction")    
    for c in b.topLevelComponents():
      self.assertEqual(c.lastAction,"anotherAction")
  def test_apply_action_to_Assemblage_from_non_empty_blueprint_applies_action_to_single_top_level_component(self):
    b = Blueprint(NoteLastAppliedAction())   
    self.assertEqual(b.topLevelComponents().lastAction,'')
    Assemblage(b).apply("Action_a")    
    self.assertEqual(b.topLevelComponents().lastAction,'Action_a')
    Assemblage(b).apply("JustDoIt")    
    self.assertEqual(b.topLevelComponents().lastAction,"JustDoIt")
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
    for c in binner.topLevelComponents():
      self.assertEqual(c.lastAction,'')
    bouter = Blueprint(Assemblage(binner))
    for c in binner.topLevelComponents():
      self.assertEqual(c.lastAction,'')
    Assemblage(bouter).apply("anAction")    
    for c in binner.topLevelComponents():
      self.assertEqual(c.lastAction,'anAction')
    Assemblage(bouter).apply("anotherAction")    
    for c in binner.topLevelComponents():
      self.assertEqual(c.lastAction,"anotherAction")

if __name__ == '__main__':
  unittest.main()

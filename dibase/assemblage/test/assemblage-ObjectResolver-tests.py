#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.resolver.ObjectResolver tests 
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
from dibase.assemblage.resolvers import ObjectResolver

class TestType:
  CustomPattern="custom_%(actionName)s_%(fnName)s"
  def __init__(self):
    self.fnAction = None
    self.customPattern = False
  def action_method(self):
    self.fnAction = 'action'
  def anotherAction_method(self):
    self.fnAction = 'anotherAction'
  def custom_action_method(self):
    self.fnAction = 'action'
    self.customPattern = True
  def custom_anotherAction_method(self):
    self.fnAction = 'anotherAction'
    self.customPattern = True

class TestResolver:
  def __init__(self, actionName, args):
    self.actionName = actionName
    self.args = args

class TestResolverFactory:
  def create(self, actionName, **dynamicInitArgs):
    return TestResolver(actionName, dynamicInitArgs)

class TestAssemblageObjectResolver(unittest.TestCase):
  def test_ObjectResolver_default_pattern(self):
    rAction = ObjectResolver('action')
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fnAction, 'action')
    self.assertFalse(object.customPattern)
    rAnotherAction = ObjectResolver('anotherAction')
    object2 = TestType()
    fn = rAnotherAction.resolve('method',object2)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object2.fnAction, 'anotherAction')
    self.assertFalse(object2.customPattern)
  def test_ObjectResolver_custom_pattern(self):
    rAction = ObjectResolver('action', TestType.CustomPattern)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fnAction, 'action')
    self.assertTrue(object.customPattern)
    rAnotherAction = ObjectResolver('anotherAction', fnNamePattern=TestType.CustomPattern)
    object2 = TestType()
    fn = rAnotherAction.resolve('method',object2)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object2.fnAction, 'anotherAction')
    self.assertTrue(object2.customPattern)
  def test_ObjectResolver_default_pattern_not_resolved_returns_None(self):
    rAction = ObjectResolver('action')
    object = TestType()
    fn = rAction.resolve('no_method',object)
    self.assertIsNone(fn)
  def test_ObjectResolver_custom_pattern_not_resolved_returns_None(self):
    rAction = ObjectResolver('action', TestType.CustomPattern)
    object = TestType()
    fn = rAction.resolve('no_method',object)
    self.assertIsNone(fn)
  def test_ObjectResolver_default_pattern_created_with_extraneous_named_arguments(self):
    rAction = ObjectResolver('action', spare1=1, spare2=2)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fnAction, 'action')
    self.assertFalse(object.customPattern)
  def test_ObjectResolver_custom_pattern_created_with_extraneous_named_arguments(self):
    rAction = ObjectResolver('action', fnNamePattern=TestType.CustomPattern, spare1=1, spare2=2)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fnAction, 'action')
    self.assertTrue(object.customPattern)

if __name__ == '__main__':
  unittest.main()

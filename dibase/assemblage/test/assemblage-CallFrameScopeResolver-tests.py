#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.resolver.CallFrameScopeResolver tests 
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
from dibase.assemblage.resolvers import CallFrameScopeResolver

class TestAction:
  @staticmethod
  def method(object):
    object.cls = '(module)TestAction'
    object.fn = 'method'
  @classmethod
  def altMethod(cls, object):
    object.cls = '(module)TestAction'
    object.fn = 'altMethod'

class custom_TestAction:
  @staticmethod
  def custom_method(object):
    object.cls = '(module)custom_TestAction'
    object.fn = 'custom_method'
  @classmethod
  def custom_altMethod(cls, object):
    object.cls = '(module)custom_TestAction'
    object.fn = 'custom_altMethod'

class TestType:
  def __init__(self):
    self.cls = None
    self.fn = None

class TestAssemblageCallFrameScopeResolver(unittest.TestCase):
  def test_CallFrameScopeResolver_default_patterns_no_class_returns_None(self):
    rAction = CallFrameScopeResolver('NoActionClass', frameNumber=1)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNone(fn)
  def test_CallFrameScopeResolver_default_patterns_no_function_returns_None(self):
    rAction = CallFrameScopeResolver('TestAction', frameNumber=1)
    object = TestType()
    fn = rAction.resolve('no_method',object)
    self.assertIsNone(fn)
  def test_CallFrameScopeResolver_default_patterns_module_scope_class_with_function_returns_method(self):
    rAction = CallFrameScopeResolver('TestAction', frameNumber=1)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fn, 'method')
    self.assertEqual(object.cls, '(module)TestAction')
    object2 = TestType()
    fn = rAction.resolve('altMethod',object2)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object2.fn, 'altMethod')
    self.assertEqual(object2.cls, '(module)TestAction')
  def test_CallFrameScopeResolver_custom_patterns_module_scope_class_with_function_returns_method(self):
    rAction = CallFrameScopeResolver('TestAction', frameNumber=1, fnNamePattern="custom_%(fnName)s", clsNamePattern="custom_%(actionName)s")
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fn, 'custom_method')
    self.assertEqual(object.cls, '(module)custom_TestAction')
    object2 = TestType()
    fn = rAction.resolve('altMethod',object2)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object2.fn, 'custom_altMethod')
    self.assertEqual(object2.cls, '(module)custom_TestAction')
  def test_CallFrameScopeResolver_default_patterns_local_scope_class_with_function_returns_method(self):
    class TestAction:
      @staticmethod
      def method(object):
        object.cls = '(local)TestAction'
        object.fn = 'method'
      @classmethod
      def altMethod(cls, object):
        object.cls = '(local)TestAction'
        object.fn = 'altMethod'
    rAction = CallFrameScopeResolver('TestAction', frameNumber=1)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fn, 'method')
    self.assertEqual(object.cls, '(local)TestAction')
    object2 = TestType()
    fn = rAction.resolve('altMethod',object2)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object2.fn, 'altMethod')
    self.assertEqual(object2.cls, '(local)TestAction')
  class ClassTestAction:
    @staticmethod
    def method(object):
      object.cls = '(class)ClassTestAction'
      object.fn = 'method'
    @classmethod
    def altMethod(cls, object):
      object.cls = '(class)ClassTestAction'
      object.fn = 'altMethod'
  def test_CallFrameScopeResolver_default_patterns_methodClass_scope_class_with_function_returns_method(self):
    rAction = CallFrameScopeResolver('ClassTestAction', frameNumber=1)
    object = TestType()
    fn = rAction.resolve('method',object)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object.fn, 'method')
    self.assertEqual(object.cls, '(class)ClassTestAction')
    object2 = TestType()
    fn = rAction.resolve('altMethod',object2)
    self.assertIsNotNone(fn)
    fn()
    self.assertEqual(object2.fn, 'altMethod')
    self.assertEqual(object2.cls, '(class)ClassTestAction')

if __name__ == '__main__':
  unittest.main()

#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.component.Component 
"""
import unittest
import io
import logging
import inspect

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from component import Component

class TestAssemblageComponent(unittest.TestCase):
  log_level = logging.INFO 
#  log_level = logging.DEBUG
  log_output = io.StringIO()
  logger = None
  show_log = False
  @classmethod
  def clearLog(cls):
    cls.log_output.truncate(0);
    cls.log_output.seek(0)
  @classmethod
  def setUpClass(cls):
    cls.logger = logging.getLogger("TestAssemblageComponent")
    cls.logger.propagate = False
    if not cls.logger.hasHandlers():
      loghdr = logging.StreamHandler(stream=cls.log_output)
      formatter = logging.Formatter('%(levelname)s: %(message)s')
      loghdr.setFormatter(formatter)
      cls.logger.addHandler(loghdr)
      cls.logger.setLevel(cls.log_level)
  def setUp(self):
    self.clearLog();
  def tearDown(self):
    if self.show_log:
      print("|%s|\n"%self.log_output.getvalue())
      self.show_log = False
    self.clearLog();

  def test_basic_component_compares_equal_to_name_can_write_to_logger_and_has_no_elements(self):
    c = Component("test")
    self.assertEqual(c, "test")
    self.assertNotEqual(repr(c).find('elements=[])'),-1)
  def test_basic_component_string_representation_is_name(self):
    c = Component("test")
    self.assertEqual(str(c), "test")
  def test_equals_between_two_components(self):
    c = Component('CCC')
    d = Component('DDDD')
    c2 = Component('CCC')
    self.assertTrue(c==c2)
    self.assertTrue(c==c)
    self.assertFalse(c==d)
  def test_equals_between_component_and_string(self):
    c = Component('CCC')
    cstr = 'CCC'
    d = Component('DDDD')
    self.assertTrue(c==cstr)
    self.assertTrue(cstr==c)
    self.assertFalse(d==cstr)
    self.assertFalse(cstr==d)
  def test_not_equals_between_two_components(self):
    c = Component('cccccccc')
    d = Component('DDDD')
    c2 = Component('cccccccc')
    self.assertFalse(c!=c2)
    self.assertFalse(c!=c)
    self.assertTrue(c!=d)
  def test_not_equals_between_component_and_string(self):
    c = Component('CcCcC')
    cstr = 'CcCcC'
    d = Component('DDDD')
    self.assertFalse(c!=cstr)
    self.assertFalse(cstr!=c)
    self.assertTrue(d!=cstr)
    self.assertTrue(cstr!=d)
  def test_less_than_between_two_components(self):
    c = Component('CCC')
    d = Component('DDD')
    c2 = Component('CCC')
    self.assertFalse(c<c2)
    self.assertFalse(c<c)
    self.assertFalse(d<c)
    self.assertTrue(c<d)
  def test_less_than_between_component_and_string(self):
    c = Component('ccc')
    cstr = 'ccc'
    d = Component('ddd')
    dstr = 'ddd'
    self.assertFalse(c<cstr)
    self.assertFalse(cstr<c)
    self.assertFalse(d<cstr)
    self.assertFalse(dstr<c)
    self.assertTrue(cstr<d)
    self.assertTrue(c<dstr)
  def test_less_than_or_equal_between_two_components(self):
    c = Component('CCC')
    d = Component('DDD')
    c2 = Component('CCC')
    self.assertTrue(c<=c2)
    self.assertTrue(c<=c)
    self.assertFalse(d<=c)
    self.assertTrue(c<=d)
  def test_less_than_or_equal_between_component_and_string(self):
    c = Component('ccc')
    cstr = 'ccc'
    d = Component('ddd')
    dstr = 'ddd'
    self.assertTrue(c<=cstr)
    self.assertTrue(cstr<=c)
    self.assertFalse(d<=cstr)
    self.assertFalse(dstr<=c)
    self.assertTrue(cstr<=d)
    self.assertTrue(c<=dstr)
  def test_greater_than_between_two_components(self):
    c = Component('CCC')
    d = Component('DDD')
    c2 = Component('CCC')
    self.assertFalse(c>c2)
    self.assertFalse(c>c)
    self.assertTrue(d>c)
    self.assertFalse(c>d)
  def test_greater_than_between_component_and_string(self):
    c = Component('ccc')
    cstr = 'ccc'
    d = Component('ddd')
    dstr = 'ddd'
    self.assertFalse(c>cstr)
    self.assertFalse(cstr>c)
    self.assertTrue(d>cstr)
    self.assertTrue(dstr>c)
    self.assertFalse(cstr>d)
    self.assertFalse(c>dstr)
  def test_greater_than_or_equal_between_two_components(self):
    c = Component('CCC')
    d = Component('DDD')
    c2 = Component('CCC')
    self.assertTrue(c>=c2)
    self.assertTrue(c>=c)
    self.assertTrue(d>=c)
    self.assertFalse(c>=d)
  def test_greater_than_or_equal_between_component_and_string(self):
    c = Component('ccc')
    cstr = 'ccc'
    d = Component('ddd')
    dstr = 'ddd'
    self.assertTrue(c>=cstr)
    self.assertTrue(cstr>=c)
    self.assertTrue(d>=cstr)
    self.assertTrue(dstr>=c)
    self.assertFalse(cstr>=d)
    self.assertFalse(c>=dstr)
  def test_Component_logs_to_logger_passed_in_construction(self):
    with self.assertLogs(self.logger,logging.DEBUG):
      Component("test", logger=self.logger)
    Component("test", logger=self.logger)
    print("\ntest_Component_logs_to_logger_passed_in_construction"
          "\n  INFORMATION: Component construction logged:\n    ",end='')
    self.show_log = True
  def test_calling_apply_with_unsupported_action_causes_no_errors(self):
#    self.show_log = True
    Component ( 'test-root'
              , elements=[Component('testchild', logger=self.logger)]
              , logger=self.logger
              ).apply('noSuchAction')
  def test_apply_does_no_action_steps_methods_if_query_action_methods_return_True_for_subclass_methods(self):
    class NeverDoAnyProcessingComponent(Component):
      def __init__(self,name,elements=[],logger=None):
        self.query_before = False
        self.query_after = False
        self.query_elements = False
        self.before = False
        self.after = False
        self.apply_called = False
        super().__init__(name,elements,logger)
      def someAction_queryDoBeforeElementsActions(self):
        self.query_before = True
        return False
      def someAction_queryDoAfterElementsActions(self):
        self.query_after = True
        return False
      def someAction_queryProcessElements(self):
        self.query_elements = True
        return False
      def someAction_beforeElementsActions(self):
        self.before = True
      def someAction_afterElementsActions(self):
        self.after = True
      def apply(self,action):
        self.apply_called = True
        super().apply(action)
#    self.show_log = True
    child = NeverDoAnyProcessingComponent('child', logger=self.logger)
    root = NeverDoAnyProcessingComponent('root',elements=[child], logger=self.logger)
    root.apply('someAction')
    self.assertTrue(root.apply_called)
    self.assertTrue(root.query_before)
    self.assertTrue(root.query_after)
    self.assertTrue(root.query_elements)
    self.assertFalse(root.before)
    self.assertFalse(root.after)
    self.assertFalse(child.apply_called)
    self.assertFalse(child.before)
    self.assertFalse(child.after)
    self.assertFalse(child.query_before)
    self.assertFalse(child.query_after)
    self.assertFalse(child.query_elements)
  def test_apply_does_action_steps_methods_if_query_action_methods_return_True_for_subclass_methods(self):
    class AlwaysDoAllComponent(Component):
      def __init__(self,name,elements=[],logger=None):
        self.query_before = False
        self.query_after = False
        self.query_elements = False
        self.before = False
        self.after = False
        self.apply_called = False
        super().__init__(name,elements,logger)
      def someAction_queryDoBeforeElementsActions(self):
        self.query_before = True
        return True
      def someAction_queryDoAfterElementsActions(self):
        self.query_after = True
        return True
      def someAction_queryProcessElements(self):
        self.query_elements = True
        return True
      def someAction_beforeElementsActions(self):
        self.before = True
      def someAction_afterElementsActions(self):
        self.after = True
      def apply(self,action):
        self.apply_called = True
        super().apply(action)
#    self.show_log = True
    child = AlwaysDoAllComponent('child', logger=self.logger)
    root = AlwaysDoAllComponent('root',elements=[child], logger=self.logger)
    root.apply('someAction')
    self.assertTrue(root.apply_called)
    self.assertTrue(root.query_before)
    self.assertTrue(root.query_after)
    self.assertTrue(root.query_elements)
    self.assertTrue(root.before)
    self.assertTrue(root.after)
    self.assertFalse(child.apply_called) # never calls back out to apply
    self.assertTrue(child.before)
    self.assertTrue(child.after)
    self.assertTrue(child.query_before)
    self.assertTrue(child.query_after)
    self.assertTrue(child.query_elements)
  def test_apply_does_no_action_steps_methods_if_query_action_methods_return_False_for_action_class_methods(self):
    class someAction:
      query_before = False
      query_after = False
      query_elements = False
      before = False
      after = False
      @classmethod
      def queryDoBeforeElementsActions(cls,element):
        cls.query_before = True
        return False
      @classmethod
      def queryDoAfterElementsActions(cls,element):
        cls.query_after = True
        return False
      @classmethod
      def queryProcessElements(cls,element):
        cls.query_elements = True
        return False
      @classmethod
      def beforeElementsActions(cls,element):
        cls.before = True
      @classmethod
      def afterElementsActions(cls,element):
        cls.after = True
#    self.show_log = True
    child = Component('child', logger=self.logger)
    root = Component('root',elements=[child], logger=self.logger)
    root.apply('someAction')
    self.assertTrue(someAction.query_before)
    self.assertTrue(someAction.query_after)
    self.assertTrue(someAction.query_elements)
    self.assertFalse(someAction.before)
    self.assertFalse(someAction.after)
  def test_apply_does_action_steps_methods_if_query_action_methods_return_True_for_action_class_methods(self):
    class someAction:
      query_before = False
      query_after = False
      query_elements = False
      before = False
      after = False
      @classmethod
      def queryDoBeforeElementsActions(cls,element):
        cls.query_before = True
        return True
      @classmethod
      def queryDoAfterElementsActions(cls,element):
        cls.query_after = True
        return True
      @classmethod
      def queryProcessElements(cls,element):
        cls.query_elements = True
        return True
      @classmethod
      def beforeElementsActions(cls,element):
        cls.before = True
      @classmethod
      def afterElementsActions(cls,element):
        cls.after = True
#    self.show_log = True
    child = Component('child', logger=self.logger)
    root = Component('root',elements=[child], logger=self.logger)
    root.apply('someAction')
    self.assertTrue(someAction.query_before)
    self.assertTrue(someAction.query_after)
    self.assertTrue(someAction.query_elements)
    self.assertTrue(someAction.before)
    self.assertTrue(someAction.after)

if __name__ == '__main__':
  unittest.main()

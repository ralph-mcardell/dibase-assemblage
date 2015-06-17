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
from interfaces import AssemblageBase, DigestCacheBase

class someModuleScopeAction:
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

class SpoofDigestCache(DigestCacheBase):
  def __init__(self):
    self.updateIfDifferentCount = 0
    self.writeBackCount = 0
  def updateIfDifferent(self, element):
    self.updateIfDifferentCount = self.updateIfDifferentCount + 1
    return False
  def writeBack(self):
    self.writeBackCount = self.writeBackCount + 1

class NullAssemblage(AssemblageBase):
  def logger(self):
    pass
  def digestCache(self):
    pass
class LoggingAssemblage(NullAssemblage):
  def logger(self):
    return logging.getLogger()
class DigestCacheAssemblage(NullAssemblage):
  def __init__(self):
    self.cache = SpoofDigestCache()
  def digestCache(self):
    return self.cache
class LoggingDigestCacheAssemblage(DigestCacheAssemblage):
  def logger(self):
    return logging.getLogger()

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
    c = Component("test", LoggingAssemblage())
    self.assertEqual(c, "test")
    self.assertNotEqual(repr(c).find('elements=[])'),-1)
  def test_basic_component_string_representation_is_name(self):
    c = Component("test", LoggingAssemblage())
    self.assertEqual(str(c), "test", LoggingAssemblage())
  def test_equals_between_two_components(self):
    c = Component('CCC', LoggingAssemblage())
    d = Component('DDDD', LoggingAssemblage())
    c2 = Component('CCC', LoggingAssemblage())
    self.assertTrue(c==c2)
    self.assertTrue(c==c)
    self.assertFalse(c==d)
  def test_equals_between_component_and_string(self):
    c = Component('CCC', LoggingAssemblage())
    cstr = 'CCC'
    d = Component('DDDD', LoggingAssemblage())
    self.assertTrue(c==cstr)
    self.assertTrue(cstr==c)
    self.assertFalse(d==cstr)
    self.assertFalse(cstr==d)
  def test_not_equals_between_two_components(self):
    c = Component('cccccccc', LoggingAssemblage())
    d = Component('DDDD', LoggingAssemblage())
    c2 = Component('cccccccc', LoggingAssemblage())
    self.assertFalse(c!=c2)
    self.assertFalse(c!=c)
    self.assertTrue(c!=d)
  def test_not_equals_between_component_and_string(self):
    c = Component('CcCcC', LoggingAssemblage())
    cstr = 'CcCcC'
    d = Component('DDDD', LoggingAssemblage())
    self.assertFalse(c!=cstr)
    self.assertFalse(cstr!=c)
    self.assertTrue(d!=cstr)
    self.assertTrue(cstr!=d)
  def test_less_than_between_two_components(self):
    c = Component('CCC', LoggingAssemblage())
    d = Component('DDD', LoggingAssemblage())
    c2 = Component('CCC', LoggingAssemblage())
    self.assertFalse(c<c2)
    self.assertFalse(c<c)
    self.assertFalse(d<c)
    self.assertTrue(c<d)
  def test_less_than_between_component_and_string(self):
    c = Component('ccc', LoggingAssemblage())
    cstr = 'ccc'
    d = Component('ddd', LoggingAssemblage())
    dstr = 'ddd'
    self.assertFalse(c<cstr)
    self.assertFalse(cstr<c)
    self.assertFalse(d<cstr)
    self.assertFalse(dstr<c)
    self.assertTrue(cstr<d)
    self.assertTrue(c<dstr)
  def test_less_than_or_equal_between_two_components(self):
    c = Component('CCC', LoggingAssemblage())
    d = Component('DDD', LoggingAssemblage())
    c2 = Component('CCC', LoggingAssemblage())
    self.assertTrue(c<=c2)
    self.assertTrue(c<=c)
    self.assertFalse(d<=c)
    self.assertTrue(c<=d)
  def test_less_than_or_equal_between_component_and_string(self):
    c = Component('ccc', LoggingAssemblage())
    cstr = 'ccc'
    d = Component('ddd', LoggingAssemblage())
    dstr = 'ddd'
    self.assertTrue(c<=cstr)
    self.assertTrue(cstr<=c)
    self.assertFalse(d<=cstr)
    self.assertFalse(dstr<=c)
    self.assertTrue(cstr<=d)
    self.assertTrue(c<=dstr)
  def test_greater_than_between_two_components(self):
    c = Component('CCC', LoggingAssemblage())
    d = Component('DDD', LoggingAssemblage())
    c2 = Component('CCC', LoggingAssemblage())
    self.assertFalse(c>c2)
    self.assertFalse(c>c)
    self.assertTrue(d>c)
    self.assertFalse(c>d)
  def test_greater_than_between_component_and_string(self):
    c = Component('ccc', LoggingAssemblage())
    cstr = 'ccc'
    d = Component('ddd', LoggingAssemblage())
    dstr = 'ddd'
    self.assertFalse(c>cstr)
    self.assertFalse(cstr>c)
    self.assertTrue(d>cstr)
    self.assertTrue(dstr>c)
    self.assertFalse(cstr>d)
    self.assertFalse(c>dstr)
  def test_greater_than_or_equal_between_two_components(self):
    c = Component('CCC', LoggingAssemblage())
    d = Component('DDD', LoggingAssemblage())
    c2 = Component('CCC', LoggingAssemblage())
    self.assertTrue(c>=c2)
    self.assertTrue(c>=c)
    self.assertTrue(d>=c)
    self.assertFalse(c>=d)
  def test_greater_than_or_equal_between_component_and_string(self):
    c = Component('ccc', LoggingAssemblage())
    cstr = 'ccc'
    d = Component('ddd', LoggingAssemblage())
    dstr = 'ddd'
    self.assertTrue(c>=cstr)
    self.assertTrue(cstr>=c)
    self.assertTrue(d>=cstr)
    self.assertTrue(dstr>=c)
    self.assertFalse(cstr>=d)
    self.assertFalse(c>=dstr)
  def test_Component_logs_to_logger_passed_in_construction(self):
    self.logger.setLevel(logging.DEBUG)
    with self.assertLogs(self.logger,logging.DEBUG):
      Component("test", NullAssemblage(), logger=self.logger)
    Component("test", NullAssemblage(), logger=self.logger)
    print("\ntest_Component_logs_to_logger_passed_in_construction"
          "\n  INFORMATION: Component construction logged:\n    ",end='')
    self.show_log = True
    self.logger.setLevel(self.log_level)
  def test_calling_apply_with_unsupported_action_causes_no_errors(self):
#    self.show_log = True
    Component ( 'test-root'
              , assemblage=NullAssemblage()  
              , elements=[Component('testchild', NullAssemblage(), logger=self.logger)]
              , logger=self.logger
              ).apply('noSuchAction')
  def test_apply_does_no_action_steps_methods_if_query_action_methods_return_True_for_subclass_methods(self):
    class NeverDoAnyProcessingComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        self.query_before = False
        self.query_after = False
        self.query_elements = False
        self.before = False
        self.after = False
        self.apply_called = False
        super().__init__(name,assm,elements,logger)
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
    child = NeverDoAnyProcessingComponent('child', NullAssemblage(), logger=self.logger)
    root = NeverDoAnyProcessingComponent('root', NullAssemblage(), elements=[child], logger=self.logger)
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
      def __init__(self,name,assm,elements=[],logger=None):
        self.query_before = False
        self.query_after = False
        self.query_elements = False
        self.before = False
        self.after = False
        self.apply_called = False
        super().__init__(name,assm,elements,logger)
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
    child = AlwaysDoAllComponent('child', NullAssemblage(), logger=self.logger)
    root = AlwaysDoAllComponent('root', NullAssemblage(), elements=[child], logger=self.logger)
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
    child = Component('child', NullAssemblage(), logger=self.logger)
    root = Component('root', NullAssemblage(), elements=[child], logger=self.logger)
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
    child = Component('child', NullAssemblage(), logger=self.logger)
    root = Component('root', NullAssemblage(), elements=[child], logger=self.logger)
    root.apply('someAction')
    self.assertTrue(someAction.query_before)
    self.assertTrue(someAction.query_after)
    self.assertTrue(someAction.query_elements)
    self.assertTrue(someAction.before)
    self.assertTrue(someAction.after)
  class someClassScopeAction:
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
  def test_apply_finds_action_class_defined_in_a_callers_outer_scope(self):
#    self.show_log = True
    child = Component('child', NullAssemblage(), logger=self.logger)
    root = Component('root', NullAssemblage(), elements=[child], logger=self.logger)
    root.apply('someClassScopeAction')
    self.assertTrue(self.someClassScopeAction.query_before)
    self.assertTrue(self.someClassScopeAction.query_after)
    self.assertTrue(self.someClassScopeAction.query_elements)
    self.assertTrue(self.someClassScopeAction.before)
    self.assertTrue(self.someClassScopeAction.after)
  def test_apply_finds_action_class_defined_in_callers_module_scope(self):
#    self.show_log = True
    child = Component('child', NullAssemblage(), logger=self.logger)
    root = Component('root', NullAssemblage(), elements=[child], logger=self.logger)
    root.apply('someModuleScopeAction')
    self.assertTrue(someModuleScopeAction.query_before)
    self.assertTrue(someModuleScopeAction.query_after)
    self.assertTrue(someModuleScopeAction.query_elements)
    self.assertTrue(someModuleScopeAction.before)
    self.assertTrue(someModuleScopeAction.after)
  def test_apply_rasies_RuntimeError_if_Component_graph_has_cirular_references(self):
#    self.show_log = True
    grandchild2_children = []
    grandchild1 = Component('grandchild1', NullAssemblage(), logger=self.logger)
    child1 = Component('child1', NullAssemblage(), elements=[grandchild1], logger=self.logger)
    grandchild2 = Component('grandchild2', NullAssemblage(), elements=grandchild2_children, logger=self.logger)
    child2 = Component('child2', NullAssemblage(), elements=[grandchild2], logger=self.logger)
    root = Component('root', NullAssemblage(), elements=[child1,child2], logger=self.logger)
    grandchild2_children.append(root) # Ooops!
    with self.assertRaises(RuntimeError):
      root.apply('someModuleScopeAction')
    try:
      root.apply('someModuleScopeAction')
    except RuntimeError as e:
      print("\ntest_apply_rasies_RuntimeError_if_Component_graph_has_cirular_references\n"
            "  INFORMATION: RuntimeError raised with message:\n     '%(e)s'" % {'e':e})

  def test_doesNotExist_returns_True(self):
    self.assertTrue(Component('test', LoggingAssemblage()).doesNotExist())
  def test_overrident_doesNotExist_returns_override_result(self):
    class ExistingComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def doesNotExist(self):
        return False
    self.assertFalse(ExistingComponent('test', LoggingAssemblage()).doesNotExist())
  def test_digest_returns_bytes_Componen(self):
    self.assertEqual(Component('test', LoggingAssemblage()).digest(),b'Componen')
  def test_overridden_digest_returns_override_result(self):
    class DigestingComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def digest(self):
        return b'Digesting'
    self.assertEqual(DigestingComponent('test', LoggingAssemblage()).digest(),b'Digesting')
  def test_hasChanged_returns_result_of_calling_assemblage_digestCache_updateIfDifferent(self):
    assm = LoggingDigestCacheAssemblage()
    self.assertFalse(Component('test', assm).hasChanged())
    self.assertEqual(assm.digestCache().updateIfDifferentCount,1)
  def test_overridden_hasChanged_returns_override_result(self):
    class ChangedComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        return True
    self.assertTrue(ChangedComponent('test', LoggingAssemblage()).hasChanged())
  def test_isOutOfDate_on_single_leaf_Component_returns_False(self):
    self.assertFalse(Component('test', LoggingDigestCacheAssemblage()).isOutOfDate())
  def test_isOutOfDate_on_single_leaf_Component_with_overridden_hasChanged_returns_hasChanged_override_result(self):
    class ChangedComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        return True
    self.assertTrue(ChangedComponent('test', LoggingAssemblage()).isOutOfDate())
  def test_isOutOfDate_on_multiple_Components_returns_True_if_any_hasChanged_on_leaf_returns_True(self):
    class NonLeafComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        self.fail("Component.IsOutOfDate called hasChanged on non-leaf element")
    class LeafComponent(Component):
      changed = False
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        self.changed = not self.changed
        return self.changed
    self.assertTrue( Component( 'test'
                              , LoggingAssemblage()
                              , elements=[ NonLeafComponent('NonLeaf-1', LoggingAssemblage()
                                                           , elements=[LeafComponent('Leaf-11', LoggingAssemblage())]
                                                           )
                                         , NonLeafComponent('NonLeaf-2', LoggingAssemblage()
                                                           , elements=[LeafComponent('Leaf-21', LoggingAssemblage())]
                                                           )
                                         ]
                              ).isOutOfDate()
                   )
  def test_isOutOfDate_on_multiple_Components_returns_False_if_no_hasChanged_on_leaf_returns_True(self):
    class NonLeafComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        self.fail("Component.IsOutOfDate called hasChanged on non-leaf element")
    class LeafComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        return False
    self.assertFalse(Component( 'test'
                              , LoggingAssemblage()
                              , elements=[ NonLeafComponent('NonLeaf-1', LoggingAssemblage()
                                                           , elements=[LeafComponent('Leaf-11', LoggingAssemblage())]
                                                           )
                                         , NonLeafComponent('NonLeaf-2', LoggingAssemblage()
                                                           , elements=[LeafComponent('Leaf-21', LoggingAssemblage())]
                                                           )
                                         ]
                              ).isOutOfDate()
                    )

if __name__ == '__main__':
  unittest.main()

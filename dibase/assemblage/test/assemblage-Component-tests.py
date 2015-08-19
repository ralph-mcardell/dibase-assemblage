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
from dibase.assemblage.component import Component
from dibase.assemblage.interfaces import AssemblageBase, DigestCacheBase
import inspect

class AlwaysDoAllComponent(Component):
  def __init__(self,name,attr,elements=[],logger=None):
    self.query_before = False
    self.query_after = False
    self.query_elements = False
    self.before = False
    self.after = False
    self.apply_called = False
    super().__init__(name,attr,elements,logger)
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

class NoActionsAction:
  pass
 
class SpoofDigestCache(DigestCacheBase):
  def __init__(self):
    self.updateIfDifferentCount = 0
    self.writeBackCount = 0
  def updateIfDifferent(self, element):
    self.updateIfDifferentCount = self.updateIfDifferentCount + 1
    return False
  def writeBack(self):
    self.writeBackCount = self.writeBackCount + 1

class SpoofResolver:
  def __init__(self, actionName, **unused):
    self.actionname = actionName
  def resolve(self, fnName, object=None):
    return getattr(object, "%(a)s_%(f)s"%{'a':self.actionname, 'f':fnName}, None)
class SpoofResolutionPlan:
  def create(self, actionName, **dynArgs):
    return SpoofResolver(actionName, **dynArgs)

testAttributes = {'__logger__' : None, '__store__' : SpoofDigestCache(), '__resolution_plan__' : SpoofResolutionPlan()}

class TestAssemblageComponent(unittest.TestCase):
#  log_level = logging.INFO 
  log_level = logging.DEBUG
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
    c = Component("test", testAttributes)
    self.assertEqual(c, "test")
    self.assertNotEqual(repr(c).find('[])}'),-1)
  def test_basic_component_string_representation_is_name(self):
    c = Component("test", testAttributes)
    self.assertEqual(str(c), "test", testAttributes)
  def test_equals_between_two_components(self):
    c = Component('CCC', testAttributes)
    d = Component('DDDD', testAttributes)
    c2 = Component('CCC', testAttributes)
    self.assertTrue(c==c2)
    self.assertTrue(c==c)
    self.assertFalse(c==d)
  def test_equals_between_component_and_string(self):
    c = Component('CCC', testAttributes)
    cstr = 'CCC'
    d = Component('DDDD', testAttributes)
    self.assertTrue(c==cstr)
    self.assertTrue(cstr==c)
    self.assertFalse(d==cstr)
    self.assertFalse(cstr==d)
  def test_not_equals_between_two_components(self):
    c = Component('cccccccc', testAttributes)
    d = Component('DDDD', testAttributes)
    c2 = Component('cccccccc', testAttributes)
    self.assertFalse(c!=c2)
    self.assertFalse(c!=c)
    self.assertTrue(c!=d)
  def test_not_equals_between_component_and_string(self):
    c = Component('CcCcC', testAttributes)
    cstr = 'CcCcC'
    d = Component('DDDD', testAttributes)
    self.assertFalse(c!=cstr)
    self.assertFalse(cstr!=c)
    self.assertTrue(d!=cstr)
    self.assertTrue(cstr!=d)
  def test_less_than_between_two_components(self):
    c = Component('CCC', testAttributes)
    d = Component('DDD', testAttributes)
    c2 = Component('CCC', testAttributes)
    self.assertFalse(c<c2)
    self.assertFalse(c<c)
    self.assertFalse(d<c)
    self.assertTrue(c<d)
  def test_less_than_between_component_and_string(self):
    c = Component('ccc', testAttributes)
    cstr = 'ccc'
    d = Component('ddd', testAttributes)
    dstr = 'ddd'
    self.assertFalse(c<cstr)
    self.assertFalse(cstr<c)
    self.assertFalse(d<cstr)
    self.assertFalse(dstr<c)
    self.assertTrue(cstr<d)
    self.assertTrue(c<dstr)
  def test_less_than_or_equal_between_two_components(self):
    c = Component('CCC', testAttributes)
    d = Component('DDD', testAttributes)
    c2 = Component('CCC', testAttributes)
    self.assertTrue(c<=c2)
    self.assertTrue(c<=c)
    self.assertFalse(d<=c)
    self.assertTrue(c<=d)
  def test_less_than_or_equal_between_component_and_string(self):
    c = Component('ccc', testAttributes)
    cstr = 'ccc'
    d = Component('ddd', testAttributes)
    dstr = 'ddd'
    self.assertTrue(c<=cstr)
    self.assertTrue(cstr<=c)
    self.assertFalse(d<=cstr)
    self.assertFalse(dstr<=c)
    self.assertTrue(cstr<=d)
    self.assertTrue(c<=dstr)
  def test_greater_than_between_two_components(self):
    c = Component('CCC', testAttributes)
    d = Component('DDD', testAttributes)
    c2 = Component('CCC', testAttributes)
    self.assertFalse(c>c2)
    self.assertFalse(c>c)
    self.assertTrue(d>c)
    self.assertFalse(c>d)
  def test_greater_than_between_component_and_string(self):
    c = Component('ccc', testAttributes)
    cstr = 'ccc'
    d = Component('ddd', testAttributes)
    dstr = 'ddd'
    self.assertFalse(c>cstr)
    self.assertFalse(cstr>c)
    self.assertTrue(d>cstr)
    self.assertTrue(dstr>c)
    self.assertFalse(cstr>d)
    self.assertFalse(c>dstr)
  def test_greater_than_or_equal_between_two_components(self):
    c = Component('CCC', testAttributes)
    d = Component('DDD', testAttributes)
    c2 = Component('CCC', testAttributes)
    self.assertTrue(c>=c2)
    self.assertTrue(c>=c)
    self.assertTrue(d>=c)
    self.assertFalse(c>=d)
  def test_greater_than_or_equal_between_component_and_string(self):
    c = Component('ccc', testAttributes)
    cstr = 'ccc'
    d = Component('ddd', testAttributes)
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
      Component("test", {}, logger=self.logger)
    Component("test", {}, logger=self.logger)
    print("\ntest_Component_logs_to_logger_passed_in_construction"
          "\n  INFORMATION: Component construction logged:\n    ",end='')
    self.show_log = True
    self.logger.setLevel(self.log_level)
  def test_Component_logs_to_logger_passed_in_construction_by_name(self):
    self.logger.setLevel(logging.DEBUG)
    with self.assertLogs(self.logger,logging.DEBUG):
      Component("test", testAttributes, logger="TestAssemblageComponent")
    self.logger.setLevel(self.log_level)
  def test_Component_logs_to_passed_assemblage_logger_if_no_logger_argument_given(self):
    self.logger.setLevel(logging.DEBUG)
    with self.assertLogs(self.logger,logging.DEBUG):
      Component("test", {'__logger__':self.logger})
    self.logger.setLevel(self.log_level)
  def test_calling_apply_with_unsupported_action_causes_no_errors(self):
#    self.show_log = True
    Component ( 'test-root'
              , attributes = testAttributes
              , elements=[Component('testchild', {}, logger=self.logger)]
              , logger=self.logger
              ).apply('noSuchAction')
  def test_apply_does_no_action_steps_methods_if_query_action_methods_return_False_for_subclass_methods(self):
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
    child = NeverDoAnyProcessingComponent('child', testAttributes, logger=self.logger)
    root = NeverDoAnyProcessingComponent('root', testAttributes, elements=[child], logger=self.logger)
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
      def __init__(self,name,attr,elements=[],logger=None):
        self.query_before = False
        self.query_after = False
        self.query_elements = False
        self.before = False
        self.after = False
        self.apply_called = False
        super().__init__(name,attr,elements,logger)
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
    child = AlwaysDoAllComponent('child', testAttributes, logger=self.logger)
    root = AlwaysDoAllComponent('root', testAttributes, elements=[child], logger=self.logger)
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
  def test_apply_rasies_RuntimeError_if_Component_graph_has_cirular_references(self):
  #  self.show_log = True
    grandchild2_children = []
    grandchild1 = AlwaysDoAllComponent('grandchild1', testAttributes, logger=self.logger)
    child1 = AlwaysDoAllComponent('child1', testAttributes, elements=[grandchild1], logger=self.logger)
    grandchild2 = AlwaysDoAllComponent('grandchild2', testAttributes, elements=grandchild2_children, logger=self.logger)
    child2 = AlwaysDoAllComponent('child2', testAttributes, elements=[grandchild2], logger=self.logger)
    root = AlwaysDoAllComponent('root', testAttributes, elements=[child1,child2], logger=self.logger)
    grandchild2_children.append(root) # Ooops!
    with self.assertRaises(RuntimeError):
      root.apply('someAction')
    try:
      root.apply('someAction')
    except RuntimeError as e:
      print("\ntest_apply_rasies_RuntimeError_if_Component_graph_has_cirular_references\n"
            "  INFORMATION: RuntimeError raised with message:\n     '%(e)s'" % {'e':e})

  def test_doesNotExist_returns_True(self):
    self.assertTrue(Component('test', testAttributes).doesNotExist())
  def test_overrident_doesNotExist_returns_override_result(self):
    class ExistingComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def doesNotExist(self):
        return False
    self.assertFalse(ExistingComponent('test', testAttributes).doesNotExist())
  def test_digest_returns_bytes_Componen(self):
    self.assertEqual(Component('test', testAttributes).digest(),b'Componen')
  def test_overridden_digest_returns_override_result(self):
    class DigestingComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def digest(self):
        return b'Digesting'
    self.assertEqual(DigestingComponent('test', testAttributes).digest(),b'Digesting')
  def test_hasChanged_returns_result_of_calling_assemblage_digestCache_updateIfDifferent(self):
    self.assertFalse(Component('test', testAttributes).hasChanged())
    self.assertEqual(testAttributes['__store__'].updateIfDifferentCount,1)
  def test_overridden_hasChanged_returns_override_result(self):
    class ChangedComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        return True
    self.assertTrue(ChangedComponent('test', testAttributes).hasChanged())
  def test_isOutOfDate_on_single_leaf_Component_returns_False(self):
    self.assertFalse(Component('test', testAttributes).isOutOfDate())
  def test_isOutOfDate_on_single_leaf_Component_with_overridden_hasChanged_returns_hasChanged_override_result_after_action_applied(self):
    class ChangedComponent(AlwaysDoAllComponent):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        return True
    c = ChangedComponent('test', testAttributes)
    self.assertFalse(c.isOutOfDate())
    c.apply('someAction') # action must process sub-elements
    self.assertTrue(c.isOutOfDate())
  def test_isOutOfDate_on_multiple_Components_returns_True_after_action_applied_to_one_or_more_elements_True(self):
    class NonLeafComponent(AlwaysDoAllComponent):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        self.fail("Component.IsOutOfDate called hasChanged on non-leaf element")
    class LeafComponent(AlwaysDoAllComponent):
      changed = False
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def hasChanged(self):
        self.changed = not self.changed
        return self.changed
    c = AlwaysDoAllComponent\
                  ( 'test'
                  , testAttributes
                  , elements=[ NonLeafComponent('NonLeaf-1', testAttributes
                                               , elements=[LeafComponent('Leaf-11', testAttributes)]
                                               )
                             , NonLeafComponent('NonLeaf-2', testAttributes
                                               , elements=[LeafComponent('Leaf-21', testAttributes)]
                                               )
                             ]
                  )
    c.apply('someAction')
    self.assertTrue(c.isOutOfDate())
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
                              , testAttributes
                              , elements=[ NonLeafComponent('NonLeaf-1', testAttributes
                                                           , elements=[LeafComponent('Leaf-11', testAttributes)]
                                                           )
                                         , NonLeafComponent('NonLeaf-2', testAttributes
                                                           , elements=[LeafComponent('Leaf-21', testAttributes)]
                                                           )
                                         ]
                              ).isOutOfDate()
                    )
  def test_module_level_empty_action_class_acts_like_all_queries_return_false(self):
    class RecordElementActionsComponent(Component):
      def __init__(self,name,assm,elements=[],logger=None):
        self.before = False
        self.after = False
        super().__init__(name,assm,elements,logger)
      def NoActionsAction_beforeElementsActions(self):
        self.before = True
      def NoActionsAction_afterElementsActions(self):
        self.after = True
  
    c =  RecordElementActionsComponent\
                  ( 'test'
                  , testAttributes
                  , elements=[Component('se-1', testAttributes)]
                  )
    c.apply('NoActionsAction')
    self.assertFalse(c.before)
    self.assertFalse(c.after)
  def test_newly_constructed_Component_has_reset_action_processing_states(self):
    c =  Component( 'test'
                  , testAttributes
                  )
    self.assertFalse(c.queryBeforeElementsActionsDone())
    self.assertFalse(c.queryAfterElementsActionsDone())
  def test_apply_action_with_only_before_action_processing_queryBeforeElementsActionsDone_returns_True(self):
    class DoOnlyBeforeActions(AlwaysDoAllComponent):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def someAction_queryDoAfterElementsActions(self):
        return False
      def someAction_queryProcessElements(self):
        return False
    c = DoOnlyBeforeActions('test', testAttributes)
    c.apply('someAction')
    self.assertTrue(c.queryBeforeElementsActionsDone())
    self.assertFalse(c.queryAfterElementsActionsDone())
  def test_apply_action_with_only_after_action_processing_queryAfterElementsActionsDone_returns_True(self):
    class DoOnlyAfterActions(AlwaysDoAllComponent):
      def __init__(self,name,assm,elements=[],logger=None):
        super().__init__(name,assm,elements,logger)
      def someAction_queryDoBeforeElementsActions(self):
        return False
      def someAction_queryProcessElements(self):
        return False
    c = DoOnlyAfterActions('test', testAttributes)
    c.apply('someAction')
    self.assertFalse(c.queryBeforeElementsActionsDone())
    self.assertTrue(c.queryAfterElementsActionsDone())
  def test_apply_action_correctly_sets_both_processing_states_on_repeated_apply_calls(self):
    class DoSettableActions(AlwaysDoAllComponent):
      def __init__(self,name,assm,elements=[],logger=None):
        self.doBefore = True
        self.doAfter = True
        super().__init__(name,assm,elements,logger)
      def someAction_queryDoBeforeElementsActions(self):
        return self.doBefore
      def someAction_queryDoAfterElementsActions(self):
        return self.doAfter
      def someAction_queryProcessElements(self):
        return False
    c = DoSettableActions('test', testAttributes)
    c.apply('someAction')
    self.assertTrue(c.queryBeforeElementsActionsDone())
    self.assertTrue(c.queryAfterElementsActionsDone())
    c.doBefore = False
    c.doAfter = False
    c.apply('someAction')
    self.assertFalse(c.queryBeforeElementsActionsDone())
    self.assertFalse(c.queryAfterElementsActionsDone())
    c.doBefore = True
    c.doAfter = False
    c.apply('someAction')
    self.assertTrue(c.queryBeforeElementsActionsDone())
    self.assertFalse(c.queryAfterElementsActionsDone())
    c.doBefore = False
    c.doAfter = True
    c.apply('someAction')
    self.assertFalse(c.queryBeforeElementsActionsDone())
    self.assertTrue(c.queryAfterElementsActionsDone())
    
if __name__ == '__main__':
  unittest.main()

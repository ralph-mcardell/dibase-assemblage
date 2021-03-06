#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.Blueprint
"""
import unittest
import logging
import io
import re

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
from dibase.assemblage.blueprint import Blueprint
from dibase.assemblage.interfaces import AssemblageBase,DigestCacheBase

class TestComponent:
  def __init__(self, name, elements, logger, **kwargs):
    self.name = name
    self.elements = elements
    self.logger = logger
    self.args = kwargs
  def __lt__(self,other):
    return self.name < other.name

class NullDigestCache(DigestCacheBase):
  def updateIfDifferent(self, element):
    pass
  def writeBack(self):
    pass
class NullAssemblage(AssemblageBase):
  def _applyInner(self, action, resolver):
    pass
  def apply(self, action):
    pass
  def logger(self):
    pass
  def digestCache(self):
    pass

class TestAssemblageBlueprint(unittest.TestCase):
  log_output = io.StringIO()
  log_error  = io.StringIO()
  @classmethod
  def setUpClass(cls):
    from dibase.assemblage.logging import Logger
    from dibase.assemblage.logging import handler
    Logger.get().removeHandler(handler.stdout)
    Logger.get().removeHandler(handler.stderr)
    if Logger.get().hasHandlers():
      raise RuntimeError("ERROR: Some test left assemblage logger with handler(s) other than .logging.handler.stdout,stderr")
    handler.stdout = None
    handler.stderr = None
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = cls.log_output
    sys.stderr = cls.log_error
    handler._initHandlers()
    Blueprint().logger()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if len(cls.log_output.getvalue()) or len(cls.log_error.getvalue()):
      print("---------------------------------------------------------------------")
      print("BLUEPRINT TESTS: Initialisation stdout output:\n%s"%cls.log_output.getvalue())
      print("BLUEPRINT TESTS: Initialisation stderr output:\n%s"%cls.log_error.getvalue())
      print("---------------------------------------------------------------------")
    cls.log_output.truncate(0)
    cls.log_output.seek(0)
    cls.log_error.truncate(0)
    cls.log_error.seek(0)

  def test_default_blueprint_has_usable_default_logger(self):
    self.assertIsInstance(Blueprint().logger(), logging.Logger)
    self.assertTrue(Blueprint().logger().hasHandlers())
    print("BLUEPRINT : Logger effective level:%s"%str(Blueprint().logger().getEffectiveLevel()))
    self.assertTrue(Blueprint().logger().isEnabledFor(logging.INFO))
  def test_logger_returns_specific_logger_if_one_set_with_setlogger(self):
    stringstream = io.StringIO()
    loghdr = logging.StreamHandler(stringstream)
    formatter = logging.Formatter('SETLOGGERTEST: %(levelname)s: %(message)s')
    loghdr.setFormatter(formatter)
    log = logging.getLogger('.'.join([__name__, "test_logger_returns_specific_logger_if_one_set_with_setlogger"]))
    log.addHandler(loghdr)
    log.setLevel(logging.DEBUG)
    b = Blueprint()
    b.setLogger(log)
    self.assertTrue(b.logger().isEnabledFor(logging.DEBUG))
    b.logger().debug('Oops!')
    self.assertEqual(stringstream.getvalue(),'SETLOGGERTEST: DEBUG: Oops!\n')
  def test_setting_logger_to_None_after_logger_is_set_will_reapply_default_logger_correctly_on_next_call_to_logger(self):
    b = Blueprint()
    self.assertIsInstance(b.logger(), logging.Logger)
    b.setLogger(None)
    self.assertIsInstance(b.logger(), logging.Logger)
    b.setLogger(None)    
    self.assertTrue(b.logger().hasHandlers())
    b.setLogger(None)    
    self.assertTrue(b.logger().isEnabledFor(logging.INFO))
    b.logger().info("MULTIPLE DEFAULT LOGGER HANDLERS TEST")
    self.assertEqual(self.log_output.getvalue().count('\n'), 0) # only .logging.OUTPUT level messages logged to stdout
    self.assertEqual(self.log_error.getvalue().count('\n'), 1) # logging.INFO...CRITICAL level messages logged to stderr
  def test_setDigestCache_object_returned_by_digestCache(self):
    b = Blueprint()
    dg = NullDigestCache()
    b.setDigestCache(dg)
    self.assertIs(b.digestCache(), dg)
  def test_topLevelElements_returned_value_is_convertible_to_False_if_no_elements_added(self):
    self.assertFalse(Blueprint().topLevelElements())
  def test_topLevelElements_returns_properly_initialised_element_if_one_added(self):
    b = Blueprint()
    b.addElements('testelement',TestComponent)
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement')
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_topLevelElements_returns_properly_initialised_element_if_one_added_to_group(self):
    b = Blueprint()
    b.addElements('testelement',TestComponent, group="testgroup")
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement')
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_topLevelElements_returns_element_with_additional_initialisation_parameters_passed_if_one_added(self):
    b = Blueprint()
    b.addElements('testelement',TestComponent, custom_arg='custom', another_arg='arg2')
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom')
      self.assertEqual(e.args['another_arg'], 'arg2')
  def test_topLevelElements_returns_element_with_additional_specific_initialisation_parameters_passed_if_one_added(self):
    class LocalComponent:
      def __init__(self, name, attributes, elements, logger, arg1, arg2):
        self.name = name
        self.elements = elements
        self.logger = logger
        self.arg1 = arg1
        self.arg2 = arg2
    b = Blueprint()
    b.addElements('testelement',LocalComponent, arg1='custom', arg2='arg2')
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertEqual(e.arg1, 'custom')
      self.assertEqual(e.arg2, 'arg2')
  def test_topLevelElements_returns_properly_initialised_elements_if_some_added(self):
    b = Blueprint()
    b.addElements('testelement1',TestComponent)
    b.addElements('testelement2',TestComponent)
    b.addElements('testelement3',TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_topLevelElements_returns_properly_initialised_elements_if_some_added_and_are_group_members(self):
    b = Blueprint()
    b.addElements('testelement1',TestComponent)
    b.addElements('testelement2',TestComponent, group="G1")
    b.addElements('testelement3',TestComponent, group="G2")
    b.addElements('testelement4',TestComponent, group="G1")
    b.addElements('testelement5',TestComponent)
    b.addElements('testelement6',TestComponent, group="G2")
    self.assertEqual(len(b.topLevelElements()),6)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_topLevelElements_returns_elements_with_additional_initialisation_parameters_passed_if_some_added(self):
    b = Blueprint()
    b.addElements('testelement1',TestComponent, custom_arg='custom1', another_arg='arg2-1')
    b.addElements('testelement2',TestComponent, custom_arg='custom2', another_arg='arg2-2')
    b.addElements('testelement3',TestComponent, custom_arg='custom3', another_arg='arg2-3')
    tle = b.topLevelElements()
    self.assertEqual(len(tle),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom%(n)d' % {'n':n})
      self.assertEqual(e.args['another_arg'], 'arg2-%(n)d' % {'n':n})
  def test_topLevelElements_returns_elements_with_additional_specific_initialisation_parameters_passed_if_some_added(self):
    class LocalComponent:
      def __init__(self, name, attributes, elements, logger, arg1, arg2):
        self.name = name
        self.elements = elements
        self.logger = logger
        self.arg1 = arg1
        self.arg2 = arg2
      def __lt__(self,other):
        return self.name < other.name
    b = Blueprint()
    b.addElements('testelement1',LocalComponent, arg1='custom1', arg2='arg2-1')
    b.addElements('testelement2',LocalComponent, arg1='custom2', arg2='arg2-2')
    b.addElements('testelement3',LocalComponent, arg1='custom3', arg2='arg2-3')
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertEqual(e.arg1, 'custom%(n)d' % {'n':n})
      self.assertEqual(e.arg2, 'arg2-%(n)d' % {'n':n})
  def test_topLevelElements_returns_single_element_if_one_added_with_another_as_subelement_root_defined_last(self):
    b = Blueprint()
    b.addElements('rootDependsOn',TestComponent)
    b.addElements('root',TestComponent, elements='rootDependsOn')
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'root')
      self.assertIs(e.logger, b.logger())
      self.assertTrue(e.elements)
      self.assertEqual(len(e.elements),1)
      for sub in e.elements:
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'rootDependsOn')
        self.assertIs(sub.logger, b.logger())
  def test_topLevelElements_returns_single_element_if_one_added_with_another_as_subelement_root_defined_first(self):
    b = Blueprint()
    b.addElements('root',TestComponent, elements='rootDependsOn')
    b.addElements('rootDependsOn',TestComponent)
    self.assertEqual(len(b.topLevelElements()),1)
    for e in b.topLevelElements():
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'root')
      self.assertIs(e.logger, b.logger())
      self.assertTrue(e.elements)
      self.assertEqual(len(e.elements),1)
      for sub in e.elements:
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'rootDependsOn')
        self.assertIs(sub.logger, b.logger())
        self.assertFalse(sub.elements)
  def test_adding_element_with_same_name_as_a_previously_added_element_raises_exception(self):
    b = Blueprint()
    b.addElements('attempted_duplicate_name',TestComponent)
    b.addElements('some_other_name',TestComponent)
    with self.assertRaises(RuntimeError):
      b.addElements('attempted_duplicate_name',TestComponent)
    try:
      b.addElements('attempted_duplicate_name',TestComponent)
    except RuntimeError as e:
      print("\ntest_adding_element_with_same_name_as_a_previously_added_element_raises_exception\n"
            "  INFORMATION: RuntimeError raised with message:\n     '%(e)s'" % {'e':e})
  def test_topLevelElements_raises_exception_if_named_subelement_not_added_as_element(self):
    b = Blueprint()
    b.addElements('root',TestComponent, elements='root_required_element_but_not_defined')
    with self.assertRaises(RuntimeError):
      b.topLevelElements()
    try:
      b.topLevelElements()
    except RuntimeError as e:
      print("\ntest_topLevelElements_raises_exception_if_named_subelement_not_added_as_element\n"
            "  INFORMATION: RuntimeError raised with message:\n     '%(e)s'" % {'e':e})
  def test_topLevelElements_returns_all_elements_if_multiple_added_in_one_addElements_call(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent)
    tle = b.topLevelElements()
    self.assertEqual(len(tle),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_topLevelElements_returns_all_elements_if_multiple_added_in_one_addElements_call_as_group_members(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent, group="G1")
    b.addElements(['testelement4', 'testelement5','testelement6'],TestComponent, group="G2")
    tle = b.topLevelElements()
    self.assertEqual(len(tle),6)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_same_init_parameters_passed_if_present(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent, custom_arg='custom', another_arg='arg2')
    self.assertEqual(len(b.topLevelElements()),3)
    for e in b.topLevelElements():
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom')
      self.assertEqual(e.args['another_arg'], 'arg2')
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_corresponding_init_parameters_passed_as_lists(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent, custom_arg=['custom1','custom2','custom3']
                  , another_arg=['arg2-1','arg2-2','arg2-3'])
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom%(n)d' % {'n':n})
      self.assertEqual(e.args['another_arg'], 'arg2-%(n)d' % {'n':n})
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_corresponding_init_parameters_passed_as_dicts(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent
                  , custom_arg={'testelement2':'custom2','testelement3':'custom3','testelement1':'custom1'}
                  , another_arg={'testelement3':'arg2-3','testelement1':'arg2-1','testelement2':'arg2-2'}
                 )
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIn('custom_arg', e.args)
      self.assertIn('another_arg', e.args)
      self.assertEqual(e.args['custom_arg'], 'custom%(n)d' % {'n':n})
      self.assertEqual(e.args['another_arg'], 'arg2-%(n)d' % {'n':n})
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_same_single_subelement(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent, elements='common_subelement')
    b.addElements('common_subelement',TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertIs(e.logger, b.logger())
      self.assertTrue(e.elements)
      self.assertEqual(len(e.elements),1)
      for sub in e.elements:
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'common_subelement')
        self.assertIs(sub.logger, b.logger())
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_same_multiple_subelements(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent, elements=['common_se-1','common_se-2','common_se-3'])
    b.addElements('common_se-1',TestComponent)
    b.addElements('common_se-2',TestComponent)
    b.addElements('common_se-3',TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertIs(e.logger, b.logger())
      self.assertTrue(e.elements)
      self.assertEqual(len(e.elements),3)
      m = 0
      for sub in sorted(e.elements):
        m = m + 1
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'common_se-%(m)d' % {'m':m})
        self.assertIs(sub.logger, b.logger())
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_corresponding_subelement_passed_as_lists(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent
                  , elements=[[],['custom21'],['custom31','custom32']]
                 )
    b.addElements('custom21',TestComponent)
    b.addElements('custom31',TestComponent)
    b.addElements('custom32',TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      self.assertEqual(len(e.elements),n)
      n = n + 1
      m = 0
      for sub in sorted(e.elements):
        m = m + 1
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'custom%(n)d%(m)d' % {'n':n,'m':m})
        self.assertIs(sub.logger, b.logger())
  def test_topLevelElements_returns_all_elements_from_addElements_call_with_corresponding_subelement_passed_as_dicts(self):
    b = Blueprint()
    b.addElements(['testelement1', 'testelement2','testelement3'],TestComponent
                  , elements={'testelement2':['custom21'],'testelement3':['custom31','custom32'],'testelement1':[]}
                 )
    b.addElements('custom21',TestComponent)
    b.addElements('custom31',TestComponent)
    b.addElements('custom32',TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertEqual(len(e.elements),n-1)
      m = 0
      for sub in sorted(e.elements):
        m = m + 1
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'custom%(n)d%(m)d' % {'n':n,'m':m})
        self.assertIs(sub.logger, b.logger())
  def test_addElements_detects_callable_for_element_names_and_passes_element_info_object_to_it_to_create_names(self):
    b = Blueprint()
    b.addElements(lambda element_data : ['testelement1', 'testelement2','testelement3'],TestComponent)
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      n = n + 1
      self.assertIsInstance(e, TestComponent)
      self.assertEqual(e.name, 'testelement%(n)d' % {'n':n})
      self.assertFalse(e.elements)
      self.assertIs(e.logger, b.logger())
  def test_addElements_detects_callable_for_element_subelements_and_passes_element_info_object_to_it_to_create_subelements(self):
    b = Blueprint()
    b.addElements( ['src1', 'src2','src3'],TestComponent,group='src')
    b.addElements( ['testelement1', 'testelement2','testelement3'],TestComponent
                 , elements=lambda element_data:[ [e] for e in sorted(element_data.elements('src'))]
                 )
    self.assertEqual(len(b.topLevelElements()),3)
    n = 0
    for e in sorted(b.topLevelElements()):
      self.assertEqual(len(e.elements),1)
      n = n + 1
      for sub in sorted(e.elements):
        self.assertIsInstance(sub, TestComponent)
        self.assertEqual(sub.name, 'src%(n)d' % {'n':n})
        self.assertIs(sub.logger, b.logger())
  def test_addElements_complex_callable_element_names_and_subelement_exercing_passed_element_data_interface(self):
    b = Blueprint()
    b.addElements( ['src1.cpp', 'src2.cpp','src3.cpp'],TestComponent,group='src')
    b.addElements( ['src1.h', 'src2.h','src3.h'],TestComponent,group='src-hdrs')
    b.addElements( ['xxx', 'yyy','zzz'],TestComponent,group='xyzzy')
    b.addElements( ['abc', '123','stuff'],TestComponent)
    def make_names_list(ed):
      names = []
      to_change = re.compile('.cpp$')
      grp = 'cpluplus' if ed.has_group('cppluplus') else 'src'
      idx = 1
      for name in ed.elements(grp):
        if ed.has_element(grp,'%(g)s%(i)d.cpp' % {'g':grp,'i':idx}):
          names.append(to_change.sub('.o',name))
        idx = idx + 1
      return names
    def make_elements_list(ed):
      elements = []
      to_change = re.compile('.cpp$')
      idx = 1
      for element in ed.elements('src'):
        if ed.has_element('src', '%(g)s%(i)d.cpp' % {'g':'src','i':idx}):
          elements.append([element,to_change.sub('.h',element)])
        idx = idx + 1
      return elements
    b.addElements( make_names_list,TestComponent
                 , elements=make_elements_list
                 )
    self.assertEqual(len(b.topLevelElements()),9) # 15 elements, 6 have parents
    n = 0
    for e in sorted(b.topLevelElements()):
      if e.name[-2:] == '.o':
        self.assertEqual(len(e.elements),2)
        n = n + 1
        m = 0
        extns = ['.cpp','.h']
        for sub in sorted(e.elements):
          self.assertIsInstance(sub, TestComponent)
          self.assertEqual(sub.name, 'src%(n)d%(e)s' % {'n':n,'e':extns[m]})
          self.assertIs(sub.logger, b.logger())
          m = m + 1
  def test_addElements_callable_parameter_function_returning_single_string_is_resolved_to_list(self):
    b = Blueprint()
    b.addElements('itIsAString', TestComponent)
    b.addElements(lambda element_data : 'testelement1',TestComponent, elements=lambda element_data:"itIsAString")
    self.assertEqual(len(b.topLevelElements()),1)
  def test_addElements_callable_parameter_function_returning_callable_returning_string_is_resolved_to_list(self):
    b = Blueprint()
    b.addElements('itIsAString', TestComponent)
    b.addElements(lambda element_data : lambda element_data: 'testelement1',TestComponent, elements=lambda element_data : lambda element_data:"itIsAString")
    self.assertEqual(len(b.topLevelElements()),1)
  def test_addElements_creates_cyclic_element_graph_raises_exception_from_topLevelElements(self):
    b = Blueprint()
    b.addElements('root', TestComponent, elements='child')
    b.addElements('child', TestComponent, elements='root')
    with self.assertRaisesRegex(RuntimeError, "^(?!.*maximum recursion)"):
      b.topLevelElements()
    try:
      b.topLevelElements()
    except RuntimeError as e:
      print("\ntest_addElements_creates_cyclic_element_graph_raises_exception_from_topLevelElements\n"
            "  INFORMATION: RuntimeError raised with message:\n     '%(e)s'" % {'e':e})
  def test_addElements_creates_non_cyclic_element_graph_with_shared_nodes_does_not_raise_exception_from_topLevelElements(self):
    b = Blueprint()
    b.addElements('root', TestComponent, elements=['child0','child1'])
    b.addElements('child0', TestComponent, elements='grandchild0')
    b.addElements('child1', TestComponent, elements='grandchild0')
    b.addElements('grandchild0', TestComponent)
    self.assertEqual(len(b.topLevelElements()),1)
  def test_addElements_adds_pre_constructed_element_objects_correctly(self):
    b = Blueprint()
    grandchildElement = TestComponent('grandchild0', elements=[], logger=b.logger())
    b.addElements('root', TestComponent, elements=['child0','child1'])
    b.addElements('child0', TestComponent, elements='grandchild0')
    b.addElements('child1', TestComponent, elements='grandchild0')
    b.addElements('grandchild0', grandchildElement)
    self.assertEqual(len(b.topLevelElements()),1)

if __name__ == '__main__':
  unittest.main()

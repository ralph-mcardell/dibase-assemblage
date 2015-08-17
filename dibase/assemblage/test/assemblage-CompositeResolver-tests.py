#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.resolver.CompositeResolver tests 
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
from dibase.assemblage.resolvers import CompositeResolver

def test_fn(arg):
  return arg

class Resolve_test_fn:
  def resolve(self, fnName, object=None):
    return test_fn if fnName == 'test_fn' else None
class ResolveMethod:
  def resolve(self, fnName, object):
    method = getattr(object, fnName, None)
    return method

class TestType:
  def __init__(self, arg):
    self.value = arg
  def testMethod(self, arg):
    return (self.value, arg)

class TestAssemblageCompositeResolver(unittest.TestCase):
  def test_empty_CompositeResolver_resolve_returns_None(self):
    cr = CompositeResolver([])
    self.assertIsNone(cr.resolve("test_fn", None))
  def test_single_resolver_CompositeResolver_resolve_returns_known_function(self):
    cr = CompositeResolver([Resolve_test_fn()])
    self.assertIsNotNone(cr.resolve("test_fn", None))
    self.assertEqual( cr.resolve("test_fn", None)(23), 23 )
  def test_single_resolver_CompositeResolver_resolve_returns_NOne_for_unknown_function(self):
    cr = CompositeResolver([Resolve_test_fn()])
    self.assertIsNone(cr.resolve("xxx", None))
  def test_multiple_resolver_CompositeResolver_resolve_returns_known_functions(self):
    cr = CompositeResolver([Resolve_test_fn(),ResolveMethod()])
    self.assertIsNotNone(cr.resolve("test_fn", None))
    self.assertEqual( cr.resolve("test_fn", None)(23), 23 )
    object = TestType('hello')
    self.assertIsNotNone(cr.resolve("testMethod", object))
    self.assertEqual( cr.resolve("testMethod", object)(67), ('hello',67) )
  def test_multiple_resolver_CompositeResolver_resolve_returns_None_for_unknown_function(self):
    cr = CompositeResolver([Resolve_test_fn(),ResolveMethod()])
    self.assertIsNone(cr.resolve("noSucFn", None))

if __name__ == '__main__':
  unittest.main()

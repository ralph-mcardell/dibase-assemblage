#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.resolver.ResolutionPlan tests 
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
from dibase.assemblage.resolvers import ResolutionPlan

def TestFn():
  pass

class TestCompositeResolver:
  def __init__(self, *resolvers):
    self.resolvers = resolvers

class TestResolver:
  def __init__(self, actionName, args):
    self.actionName = actionName
    self.args = args

class TestResolverFactory:
  def create(self, actionName, **dynamicInitArgs):
    return TestResolver(actionName, dynamicInitArgs)

class TestAssemblageResolutionPlan(unittest.TestCase):
  def test_ResolutionPlan_with_no_factories(self):
    rp = ResolutionPlan(planResolverClass=TestCompositeResolver)
    self.assertIsNotNone(rp.create('action'))
    self.assertIsInstance(rp.create('action'), TestCompositeResolver)
    self.assertEqual(len(rp.create('action').resolvers),0)
  def test_ResolutionPlan_with_single_factories_no_dynamic_args(self):
    rp = ResolutionPlan(TestResolverFactory(), planResolverClass=TestCompositeResolver)
    self.assertIsNotNone(rp.create('action'))
    self.assertIsInstance(rp.create('action'), TestCompositeResolver)
    self.assertEqual(len(rp.create('action').resolvers),1)
    self.assertEqual(rp.create('action').resolvers[0].actionName, 'action')
    self.assertEqual(len(rp.create('action').resolvers[0].args), 0)
  def test_ResolutionPlan_with_single_factories_with_dynamic_args(self):
    rp = ResolutionPlan(TestResolverFactory(), planResolverClass=TestCompositeResolver)
    cr = rp.create('action', first='1', second=2)
    self.assertIsNotNone(cr)
    self.assertIsInstance(cr, TestCompositeResolver)
    self.assertEqual(len(cr.resolvers),1)
    self.assertEqual(cr.resolvers[0].actionName, 'action')
    self.assertEqual(len(cr.resolvers[0].args), 2)
    self.assertEqual(cr.resolvers[0].args['first'], '1')
    self.assertEqual(cr.resolvers[0].args['second'], 2)
  def test_ResolutionPlan_with_multiple_factories_no_dynamic_args(self):
    rp = ResolutionPlan(TestResolverFactory(),TestResolverFactory(), planResolverClass=TestCompositeResolver)
    self.assertIsNotNone(rp.create('action'))
    self.assertIsInstance(rp.create('action'), TestCompositeResolver)
    self.assertEqual(len(rp.create('action').resolvers),2)
    self.assertEqual(rp.create('action').resolvers[0].actionName, 'action')
    self.assertEqual(len(rp.create('action').resolvers[0].args), 0)
    self.assertEqual(rp.create('action').resolvers[1].actionName, 'action')
    self.assertEqual(len(rp.create('action').resolvers[1].args), 0)
  def test_ResolutionPlan_with_multiple_factories_with_dynamic_args(self):
    rp = ResolutionPlan(TestResolverFactory(),TestResolverFactory(), planResolverClass=TestCompositeResolver)
    cr = rp.create('action', first='1', second=2)
    self.assertIsNotNone(cr)
    self.assertIsInstance(cr, TestCompositeResolver)
    self.assertEqual(len(cr.resolvers),2)
    self.assertEqual(cr.resolvers[0].actionName, 'action')
    self.assertEqual(len(cr.resolvers[0].args), 2)
    self.assertEqual(cr.resolvers[0].args['first'], '1')
    self.assertEqual(cr.resolvers[0].args['second'], 2)
    self.assertEqual(cr.resolvers[1].actionName, 'action')
    self.assertEqual(len(cr.resolvers[1].args), 2)
    self.assertEqual(cr.resolvers[1].args['first'], '1')
    self.assertEqual(cr.resolvers[1].args['second'], 2)


if __name__ == '__main__':
  unittest.main()

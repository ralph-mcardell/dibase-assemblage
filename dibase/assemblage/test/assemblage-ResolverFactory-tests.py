#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.resolver.ResolverFactory tests 
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
from dibase.assemblage.resolvers import ResolverFactory

class TestResolver:
  def __init__(self, actionName, args):
    self.actionName = actionName
    self.args = args

class TestAssemblageResolverFactory(unittest.TestCase):
  def test_ResolverFactory_creates_resolver_with_no_additional_init_parameters(self):
    rf = ResolverFactory(TestResolver)
    self.assertIsNotNone(rf.create('action'))
    self.assertIsInstance(rf.create('action'), TestResolver)
    self.assertEqual(rf.create('action').actionName, 'action')
    self.assertEqual(rf.create('action').args, {})
  def test_ResolverFactory_creates_resolver_with_additional_static_init_parameters(self):
    rf = ResolverFactory(TestResolver, first='one', second=2)
    self.assertIsNotNone(rf.create('action'))
    self.assertIsInstance(rf.create('action'), TestResolver)
    self.assertEqual(rf.create('action').actionName, 'action')
    self.assertEqual(rf.create('action').args, {'first':'one', 'second':2})
  def test_ResolverFactory_creates_resolver_with_additional_dynamic_init_parameters(self):
    rf = ResolverFactory(TestResolver)
    r = rf.create('action', one='first', two=2)
    self.assertIsNotNone(r)
    self.assertIsInstance(r, TestResolver)
    self.assertEqual(r.actionName, 'action')
    self.assertEqual(r.args, {'one':'first', 'two':2})
  def test_ResolverFactory_creates_resolver_with_additional_static_and_dynamic_init_parameters(self):
    rf = ResolverFactory(TestResolver, first='one', second=2)
    r = rf.create('action', three='third', four=4)
    self.assertIsNotNone(r)
    self.assertIsInstance(r, TestResolver)
    self.assertEqual(r.actionName, 'action')
    self.assertEqual(r.args, {'first':'one', 'second':2, 'three':'third', 'four':4})

if __name__ == '__main__':
  unittest.main()

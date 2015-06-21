#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.filecomponent.FileComponent
"""
import unittest
import glob

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from filecomponent import FileComponent
from interfaces import AssemblageBase

class NullAssemblage(AssemblageBase):
  def logger(self):
    pass
  def digestCache(self):
    pass

class TestAssemblageFileComponent(unittest.TestCase):
  def test_DoesNotExist_True_for_non_existent_file(self):
    fc = FileComponent("./nosuchfile.tst",NullAssemblage())
    self.assertTrue(fc.DoesNotExist())
if __name__ == '__main__':
  unittest.main()

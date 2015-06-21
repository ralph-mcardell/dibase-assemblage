#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.filecomponent.FileComponent
"""
import unittest
import tempfile
import glob

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from filecomponent import FileComponent
from interfaces import AssemblageBase,DigestCacheBase

class SpoofDigestCache(DigestCacheBase):
  def __init__(self):
    self.updated = {}
    self.stored = {}
  def updateIfDifferent(self, element):
    key = str(element)
    if key not in self.updated:
      self.updated[key] = self.stored[key] if key in self.stored else None
    digest = element.digest()
    if digest != self.updated[key]:
       self.updated[key] = element.digest()
       return True
    return False
  def writeBack(self):
    for uk,ud in self.updated.items():
      self.stored[uk] = ud
    self.updated = {}

class NullAssemblage(AssemblageBase):
  def logger(self):
    pass
  def digestCache(self):
    pass
class DigestCacheAssemblage(NullAssemblage):
  def __init__(self):
    self.cache = SpoofDigestCache()
  def digestCache(self):
    return self.cache

class TestAssemblageFileComponent(unittest.TestCase):
  def test_DoesNotExist_is_True_for_non_existent_file(self):
    fc = FileComponent("./nosuchfile.tst",NullAssemblage())
    self.assertTrue(fc.DoesNotExist())
  def test_DoesNotExist_is_False_for_existent_file(self):
    with tempfile.NamedTemporaryFile() as tf:
      fc = FileComponent(tf.name,NullAssemblage())
      self.assertFalse(fc.DoesNotExist())
  def test_hasChanged_True_for_new_FileComponents(self):
    tf = tempfile.NamedTemporaryFile(delete=False)
    fc = FileComponent(tf.name,DigestCacheAssemblage())
    tf.close()
    self.assertTrue(fc.hasChanged())
    os.remove(fc.normalisedPath())
if __name__ == '__main__':
  unittest.main()

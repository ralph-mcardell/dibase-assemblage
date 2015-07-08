#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.filecomponent.FileComponent 
"""
import unittest
import tempfile
import glob

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
from dibase.assemblage.filecomponent import FileComponent
from dibase.assemblage.interfaces import AssemblageBase,DigestCacheBase

class SpoofDigestCache(DigestCacheBase):
  def __init__(self):
    self.updated = {}
    self.stored = {}
    self.dirty = []
  def updateIfDifferent(self, element):
    key = str(element)
    if key not in self.updated:
      self.updated[key] = self.stored[key] if key in self.stored else None
    digest = element.digest()
    if key in self.dirty:
      return True
    if digest != self.updated[key]:
       self.updated[key] = element.digest()
       self.dirty.append(key)
       return True
    return False
  def writeBack(self):
    for uk,ud in self.updated.items():
      self.stored[uk] = ud
    self.updated = {}
    self.dirty = []

testAttributes = {'__logger__' : None, '__store__' : SpoofDigestCache()}

#class NullAssemblage(AssemblageBase):
#  def _applyInner(self, action, seen_components, callers_frame=7):
#    pass
#  def apply(self, action):
#    pass
#  def logger(self):
#    pass
#  def digestCache(self):
#    pass
#class DigestCacheAssemblage(NullAssemblage):
#  def __init__(self):
#    self.cache = SpoofDigestCache()
#  def digestCache(self):
#    return self.cache

class TestAssemblageFileComponent(unittest.TestCase):
  def test_DoesNotExist_is_True_for_non_existent_file(self):
    fc = FileComponent("./nosuchfile.tst",{})
    self.assertTrue(fc.doesNotExist())
  def test_DoesNotExist_is_False_for_existent_file(self):
    with tempfile.NamedTemporaryFile() as tf:
      fc = FileComponent(tf.name,{})
      self.assertFalse(fc.doesNotExist())
  def test_hasChanged_True_for_new_FileComponents(self):
    tf = tempfile.NamedTemporaryFile(delete=False)
    fc = FileComponent(tf.name,testAttributes)
    tf.close()
    self.assertTrue(fc.hasChanged())
    self.assertTrue(fc.hasChanged()) # still changed until written back
    os.remove(fc.normalisedPath())
  def test_hasChanged_False_for_unchanged_FileComponent_files_after_digestCache_writeBack(self):
    tf = tempfile.NamedTemporaryFile(delete=False)
    ta = testAttributes
    fc = FileComponent(tf.name,ta)
    tf.close()
    self.assertTrue(fc.hasChanged())
    ta['__store__'].writeBack()
    self.assertFalse(fc.hasChanged())
    os.remove(fc.normalisedPath())
  def test_hasChanged_True_for_changed_FileComponent_files_after_digestCache_writeBack(self):
    tf = tempfile.NamedTemporaryFile(delete=False)
    ta = testAttributes
    fc = FileComponent(tf.name,ta)
    tf.close()
    self.assertTrue(fc.hasChanged())
    ta['__store__'].writeBack()
    with open(fc.normalisedPath(), "w") as f:
      f.write("test")
    self.assertTrue(fc.hasChanged())
    os.remove(fc.normalisedPath())
  def test_hasChanged_receives_RuntimeError_if_file_does_not_exist(self):
    ta = testAttributes
    fc = FileComponent("./nosuchfile.tst",ta)
    with self.assertRaises(RuntimeError):
      fc.hasChanged()
    try:
      fc.hasChanged()
    except RuntimeError as e:
      print("\ntest_hasChanged_receives_RuntimeError_if_file_does_not_exist\n"
            "  INFORMATION: RuntimeError raised with message:\n     '%(e)s'" % {'e':e})

if __name__ == '__main__':
  unittest.main()

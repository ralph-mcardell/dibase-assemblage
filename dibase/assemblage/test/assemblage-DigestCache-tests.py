#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.digestcache.DigestCache 
"""
import unittest
import io
import logging
import inspect

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from digestcache import DigestCache
from interfaces import DigestStoreBase

class SpoofDigestStore(DigestStoreBase):
  def __init__(self, update_raises=False):
    self.store = {}
    self.update_raises = update_raises
  def retrieveDigest(self, recordName):
    return self.store[recordName] if recordName in self.store else None
  def update(self, nameDigestPairs):
    if self.update_raises:
      raise RuntimeError("SpoofDigestStore write error!!!")
    for nd in nameDigestPairs:
      self.store[nd[0]] = nd[1]

class SpoofElement:
  def __init__(self, name, digest):
    self.the_name = name
    self.the_digest = digest
  def __str__(self):
    return self.the_name
  def digest(self):
    return self.the_digest

class TestAssemblageDigestCache(unittest.TestCase):
  def test_updateIfDifferent_True_for_new_element(self):
    self.assertTrue(DigestCache(SpoofDigestStore()).updateIfDifferent(SpoofElement(name="new",digest="digest-new")))
  def test_updateIfDifferent_True_for_new_element_if_asked_a_second_time(self):
    dc = DigestCache(SpoofDigestStore())
    e = SpoofElement(name="new",digest="digest-new")
    dc.updateIfDifferent(e)
    self.assertTrue(dc.updateIfDifferent(e))
  def test_updateIfDifferent_False_for_new_element_if_asked_after_writeBack_called(self):
    ds = SpoofDigestStore()
    dc = DigestCache(ds)
    e = SpoofElement(name="new",digest="digest-new")
    self.assertTrue(dc.updateIfDifferent(e))
    dc.writeBack()
    self.assertFalse(dc.updateIfDifferent(e))
  def test_updateIfDifferent_False_for_unchanged_existing_element(self):
    ds = SpoofDigestStore()
    n = 'test'
    d = 'the digest'
    ds.store[n] = d
    self.assertIn(n, ds.store)
    self.assertEqual(ds.store[n], d)
    dc = DigestCache(ds)
    e = SpoofElement(name=n,digest=d)
    self.assertFalse(dc.updateIfDifferent(e))
  def test_updateIfDifferent_True_for_changed_existing_element(self):
    ds = SpoofDigestStore()
    n = 'test'
    existing = 'the digest'
    ds.store[n] = existing
    self.assertIn(n, ds.store)
    self.assertEqual(ds.store[n], existing)
    dc = DigestCache(ds)
    e = SpoofElement(name=n,digest="the new digest")
    self.assertTrue(dc.updateIfDifferent(e))
  def test_updateIfDifferent_True_for_changed_existing_element_if_asked_a_second_time(self):
    ds = SpoofDigestStore()
    n = 'test'
    existing = 'the digest'
    ds.store[n] = existing
    self.assertIn(n, ds.store)
    self.assertEqual(ds.store[n], existing)
    dc = DigestCache(ds)
    e = SpoofElement(name=n,digest="the new digest")
    dc.updateIfDifferent(e)
    self.assertTrue(dc.updateIfDifferent(e))
  def test_updateIfDifferent_False_for_changed_existing_element_if_asked_after_writeBack_called(self):
    ds = SpoofDigestStore()
    n = 'test'
    existing = 'the digest'
    ds.store[n] = existing
    self.assertIn(n, ds.store)
    self.assertEqual(ds.store[n], existing)
    dc = DigestCache(ds)
    e = SpoofElement(name=n,digest="the new digest")
    self.assertTrue(dc.updateIfDifferent(e))
    dc.writeBack()
    self.assertFalse(dc.updateIfDifferent(e))
  def test_updateIfDifferent_True_for_new_element_if_asked_after_writeBack_rasies(self):
    ds = SpoofDigestStore(update_raises=True)
    dc = DigestCache(ds)
    e = SpoofElement(name="new",digest="digest-new")
    self.assertTrue(dc.updateIfDifferent(e))
    with self.assertRaises(RuntimeError):
      dc.writeBack()
    self.assertTrue(dc.updateIfDifferent(e))
  def test_writeBack_writes_all_new_and_changed_digests_from_cache(self):
    ds = SpoofDigestStore()
    existing = [('exn1','exd1'), ('exn2','exd2')]
    for ex in existing:
      ds.store[ex[0]] = ex[1]
      self.assertIn(ex[0], ds.store)
      self.assertEqual(ds.store[ex[0]], ex[1])
    dc = DigestCache(ds)
    changed = [SpoofElement(name=existing[0][0],digest="changedd1")
              , SpoofElement(name='newn1',digest="newd1")
              ]
    unchanged = [SpoofElement(name=existing[1][0],digest=existing[1][1])]
    for c in changed:
      self.assertTrue(dc.updateIfDifferent(c))
      if str(c) in ds.store:
        self.assertNotEqual(ds.store[str(c)],c.digest())
    for u in unchanged:
      self.assertFalse(dc.updateIfDifferent(u))
      self.assertEqual(ds.store[str(u)],u.digest())
      
    dc.writeBack()
 
    for u in unchanged:
      self.assertFalse(dc.updateIfDifferent(u))
      self.assertEqual(ds.store[str(u)],u.digest())
    for c in changed:
      self.assertFalse(dc.updateIfDifferent(c))
      self.assertEqual(ds.store[str(c)],c.digest())

if __name__ == '__main__':
  unittest.main()

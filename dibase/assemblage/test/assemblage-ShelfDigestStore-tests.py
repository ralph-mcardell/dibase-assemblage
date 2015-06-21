#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.shelfdigeststore.ShelfDigestStore 
"""
import unittest
import glob

import os,sys
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if parent_dir not in sys.path:
  sys.path.insert(0, parent_dir)
from shelfdigeststore import ShelfDigestStore

class TestAssemblageDigestStore(unittest.TestCase):
  @staticmethod
  def storePathname():
    return 'TestAssemblageDigestStore'
  @staticmethod
  def remove_files(pathname_stem):
    filecount = 0
    for file in glob.glob(''.join([pathname_stem,'*'])):
      os.remove(file)
      filecount = filecount + 1
    return filecount
  def setUp(self):
    self.store = ShelfDigestStore(self.storePathname())
  def tearDown(self):
    filecount = self.remove_files(self.storePathname())
    self.assertNotEqual(filecount,0, "tearDown: should have removed the set of test store files.")
  def test_retrieveDigest_returns_convertible_to_False_for_new_store(self):
    self.assertFalse(self.store.retrieveDigest("whatever"))
  def test_retrieveDigest_returns_value_from_store_that_update_added(self):
    digest = b'1234567890abcdef'
    key = 't1'
    self.store.update([(key,digest)])
    self.assertEqual(self.store.retrieveDigest(key), digest)
  def test_retrieveDigest_returns_False_from_non_empty_store_for_unknown_key(self):
    digest = b'1234567890abcdef'
    key = 't1'
    self.store.update([(key,digest)])
    self.assertFalse(self.store.retrieveDigest('nosuchkey'))
  def test_retrieveDigest_returns_updated_value_from_store_that_update_updated(self):
    digest = b'1234567890abcdef'
    key = 't1'
    self.store.update([(key,b'notmostuptodate!')])
    self.store.update([(key,digest)])
    self.assertEqual(self.store.retrieveDigest(key), digest)
  def test_retrieveDigest_returns_values_from_store_that_update_added_multiple_values_to(self):
    key_digests = (['t1',b'1234567890abcdef'], ['t2',b'2234567890abcdef'], ['t3',b'3234567890abcdef'])
    self.store.update(key_digests)
    for kd in key_digests:
      self.assertEqual(self.store.retrieveDigest(kd[0]), kd[1])
  def test_retrieveDigest_returns_values_from_store_that_update_added_and_updated_multiple_values_to(self):
    key_digests1 = (['t1',b'1234567890abcdef'], ['t2',b'2234567890abcdef'], ['t3',b'3234567890abcdef'])
    key_digests2 = (['t2',b'2NEW567890abcdef'], ['t4',b'4234567890bbcdef'])
    key_digests_expected =  ( ['t1',b'1234567890abcdef'], ['t2',b'2NEW567890abcdef']
                            , ['t3',b'3234567890abcdef'], ['t4',b'4234567890bbcdef']
                            )
    self.store.update(key_digests1)
    self.store.update(key_digests2)
    for kd in key_digests_expected:
      self.assertEqual(self.store.retrieveDigest(kd[0]), kd[1])
  def test_retrieveDigest_returns_values_from_store_that_update_added_and_updated_multiple_values_to_of_mixed_types(self):
    key_digests1 = (['t1',b'1234567890abcdef'], ['t2',222222], ['t3',3234567])
    key_digests2 = (['t2','2NEW567890abcdef'], ['t4',3.1452654])
    key_digests_expected =  ( ['t1',b'1234567890abcdef'], ['t2','2NEW567890abcdef']
                            , ['t3',3234567], ['t4',3.1452654]
                            )
    self.store.update(key_digests1)
    self.store.update(key_digests2)
    for kd in key_digests_expected:
      self.assertEqual(self.store.retrieveDigest(kd[0]), kd[1])
  def test_default_path_used_if_none_provided_to_constructor(self):
    self.assertFalse(self.store.retrieveDigest("force-test-test-setUp-store-creation"))
    store = ShelfDigestStore()
    self.assertFalse(store.retrieveDigest("force-test-default-store-creation"))
    filecount = 0
    for file in glob.glob(''.join([store.defaultPath(),'*'])):
      filecount = filecount + 1
    self.assertNotEqual(filecount,0)
    self.remove_files(store.defaultPath())
if __name__ == '__main__':
  unittest.main()

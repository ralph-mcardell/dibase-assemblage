#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the DigestCache class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .interfaces import DigestCacheBase
import logging

class DigestCache(DigestCacheBase):
  '''
  Caches element resource digest values, loading and writing them back to a
  digest store supporting the DigestStoreBase interface.
  '''
  class __DigestRecord:
    '''
    Simple record type to keep dirty/clean state with a digest value.
    '''
    def __init__(self, digest, dirty):
      '''
      Store parameter values as instance data members
      '''
      self.digest = digest
      self.dirty = dirty

  def __init__(self, store):
    '''
    Initialises empty cache. The store parameter is assumed to be an object
    compatible with the DigestStoreBase interface and provides back end
    storage for cached values to be loaded and written to.
    '''
    self.__digest_store = store
    self.__cache = {}
  def __get_digest(self, element):
    '''
    Internal helper method. Looks up element digest in the cache. If not
    found asks the associated digest store to load the digest. If this fails
    as well assumes the element digest is new and adds it to the cache as a
    dirty record so it will be written to the store when writeBack is called.
    Returns the digest value.
    '''
    element_key = str(element)
    if element_key not in self.__cache:
      digest = self.__digest_store.retrieveDigest(element_key)
      if digest:
        self.__cache[element_key] = self.__DigestRecord(digest, dirty=False)
      else:
        self.__cache[element_key] = self.__DigestRecord(element.digest(), dirty=True)
    return self.__cache[element_key]

  def updateIfDifferent(self, element):
    '''
    The element parameter is assumed to adhere to the ElementBase interface.
    If the element.digest() value differs from the cached value associated
    with the element - using str(element) as the key - the new value replaces
    the old cached value and the slot marked as dirty and True is returned.
    If the element's cached digest value is found to be marked as dirty at the
    time of comparison then True is returned as it is assumed that the same
    element is being checked multiple times and so would have produced the
    same updated digest value.
    If there is no cached entry for the element's digest value an attempt is
    made to load it from the associated digest store. If this fails then it is
    assumed this is a new element and a new, dirty, entry is made for it in
    the cache and True is returned.
    '''
    cached_digest_record = self.__get_digest(element)
    if cached_digest_record.dirty:
      return True
    element_digest = element.digest()
    if element_digest!=cached_digest_record.digest:
      self.__cache[str(element)] = self.__DigestRecord(element_digest, dirty=True)
      return True
    return False
  def writeBack(self):
    '''
    Write back to the digest store the values of dirty (i.e. updated and new)
    element digests. If successful - that is the digest store update did not
    raise an exception - then all dirty cache entries are marked as clean.
    '''
    self.__digest_store.update([(k,v.digest) for k,v in self.__cache.items() if v.dirty])
    for v in self.__cache.values():
      if v.dirty:
        v.dirty = False

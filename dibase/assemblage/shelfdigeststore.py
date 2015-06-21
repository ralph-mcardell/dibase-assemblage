#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the ShelfDigestStore class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from interfaces import DigestStoreBase
import shelve

class ShelfDigestStore(DigestStoreBase):
  '''
  Digest store based on a Python shelve persistent object store.
  '''
  @staticmethod
  def defaultPath():
    '''
    Returns the default shelf store file pathname to use if a specific
    pathname is not passed to in ShelfDigestStore construction. 
    '''
    return '.__assemblage-cache__'

  def __init__(self, pathname=None):
    '''
    Creates a persistent data store using Python shelves backed by the file
    given by the pathname parameter, which if None or omitted will be the
    value of ShelfDigestStore.defaultPath()
    '''
    self.pathname = pathname if pathname else self.defaultPath()

  def update(self, nameDigestPairs):
    '''
    nameDigestPairs is a sequences of (name, digest) sequence pairs commonly
    presented as a list of tuples. The names are assumed to be unique strings
    naming an element in an assemblage. The digests are assumed to be
    pickle-able values representing a digest of the value of an element's
    associated resource.
    Each digest value is assigned to the shelf key having the associated name
    then synchronises the shelf to ensure values are written back to file.
    '''
    if nameDigestPairs:
      with shelve.open(self.pathname) as store:
        for nd in nameDigestPairs:
          store[nd[0]] = nd[1]
    
  def retrieveDigest(self, recordName):
    '''
    The recordName parameter is the key string to the digest record to be
    retrieved and returned. It is commonly the str value of an assemblage
    element. If not found None is be returned.
    '''
    digest = None
    if recordName:
      with shelve.open(self.pathname) as store:
        if recordName in store:
          digest = store[recordName]
    return digest

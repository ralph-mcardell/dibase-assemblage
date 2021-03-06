#! /usr/bin/python3
# v3.4+
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definition of the FileComponent class and related entities.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from .component import Component
import os
import hashlib
 

class FileComponent(Component):
  '''
  Component having an associated file resource in which the component name is
  the file's pathname.
  The main effect on the behaviour is to provide a digest method that returns
  an MD5 digest of the contents of the file.
  '''
  def __init__(self, name, attributes, elements=[], logger=None):
    '''
    Passes all parameters on to the Component base.
    '''
    super().__init__(name,attributes,elements,logger)
    self._path = None # filled in as late as possible
  def normalisedPath(self):
    '''
    Returns the path that is the name of the element (str(self)) with the
    user's path expanded (~) if present and normalised to be an absolute
    pathname.
    '''
    if not self._path:
      self._path = os.path.abspath(os.path.expanduser(str(self)))
    return self._path
  def doesNotExist(self):
    does_not_exist = not os.path.exists(self.normalisedPath())
    self.debug("Target file '%(f)s' does not exist? %(b)s" % {'f':self.normalisedPath(), 'b':does_not_exist})
    return does_not_exist

  def digest(self):
    '''
    Expects the path given by the component's name (str(self)) to exist then
    opens and read the file to create and return its MD5 digest.
    '''
    if self.doesNotExist():
      raise RuntimeError("FileComponent.digest: Expected file '%s' to exist"%self.normalisedPath())
    BlockSize = 65536
    hasher = hashlib.md5()
    with open(self.normalisedPath(), 'rb') as file:
        buf = file.read(BlockSize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(BlockSize)
    return hasher.digest()

#! /usr/bin/python3
''' 
Part of the dibase/assemblage package.
A tool to apply actions to multi-part constructs.
 
Definitions of various interface abstract base classes.

Developed by R.E. McArdell / Dibase Limited.
Copyright (c) 2015 Dibase Limited
License: dual: GPL or BSD.
'''

from abc import ABCMeta, abstractmethod

class AssemblageBase(metaclass=ABCMeta):
  '''
  Defines methods that are expected in an assemblage by elements (specifically
  the provided assemblage.Component class)
  '''
  @abstractmethod
  def logger(self):
    '''
    Returns a logging.Logger object. Used to access and assemblage 'default'
    logger in the case that an element is not provided with its own.
    '''
    pass
  @abstractmethod
  def digestCache(self):
    '''
    Returns an object that is of the abstract type DigestCacheBase. Used to
    access the cache of element digests that provides element resource change
    detection support
    '''
    pass

class AssemblagePlanBase(metaclass=ABCMeta):
  '''
  Defines methods that are expected in an assemblage plan that can be used to
  construct an assemblage object.
  '''
  @abstractmethod
  def logger(self):
    '''
    Returns a logging.Logger object that can be used as an assemblage object's
    logger object. 
    '''
    pass
  @abstractmethod
  def digestCache(self):
    '''
    Returns an object that is of the abstract type DigestCacheBase. Used to
    access the cache of element digests that provides element resource change
    detection support
    '''
    pass
  @abstractmethod
  def topLevelElements(self):
    '''
    Returns a single or iterable sequence of top level root elements that form
    the assemblage.
    '''
    pass

class ElementBase(metaclass=ABCMeta):
  '''
  Defines methods required by users of objects representing assemblage elements
  (the assemblage.Component class for example)
  '''
  @abstractmethod
  def apply(self, action):
    '''
    Applies action, generally a string that is a valid Python identifier,
    to element.
    '''
    pass
  @abstractmethod
  def digest(self):
    '''
    Returns a byte sequence to be used as a fixed length digest of any
    resources, such as a file, associated with an element.
    '''
    pass
  @abstractmethod
  def doesNotExist(self):
    '''
    Returns a value convertible to a Boolean value. True if an element
    resource does not exist, False if it does.
    '''
    pass
  @abstractmethod
  def hasChanged(self):
    '''
    Returns a value convertible to a Boolean value. True if an element 
    resource - without regard to its child elements - has changed with
    respect to its previously known state. False if the resource has not
    changed.
    '''
    pass
  @abstractmethod
  def isOutOfDate(self):
    '''
    Returns a value convertible to a Boolean value. True if an element
    resource is out of date with respect to its child elements.
    '''
    pass
  @abstractmethod
  def __str__(self):
    '''
    Returns a string value of the element uniquely identifying it with an
    assembly and the digest store it uses - even across executions.
    '''
    pass

class DigestCacheBase(metaclass=ABCMeta):
  '''
  Digest caches are intended to cache digests of elements' associated resources.
  It is expected that practical implementations will work in conjunction with
  some sort of persistent digest store from which element digests can be loaded
  and updated digests written back. The write back cache pattern was chosen as
  it is likely that if action steps to create a resource fail then it may not
  be appropriate to write back updated resource digests that triggered the
  action steps. It also allows grouping of update writes so may allow for
  better performance in some storage implementations.
  '''
  @abstractmethod
  def updateIfDifferent(self, element):
    '''
    The element parameter is assumed to adhere to the ElementBase interface.
    If the element.digest() value differs from the cached value (or stored
    value if not yet cached) then the cached value is updated and marked as
    dirty (i.e. will be written back by the cache writeBack method) and True
    is returned otherwise, the digests compare equal and False is returned.
    Digest values are associated with the str value of the element
    parameter. 
    '''
    pass
  @abstractmethod
  def writeBack(self):
    '''
    Write back to any associated digest store the values of dirty (i.e. updated)
    element digests.
    '''
    pass

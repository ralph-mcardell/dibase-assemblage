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

class ElementBase(metaclass=ABCMeta):
  '''
  Defines methods required by users of objects representing assemblage elements
  (the assemblage.Assemblage and assemblage.Component classes for example)
  '''
  @abstractmethod
  def apply(self, action):
    '''
    Applies action, generally a string that is a valid Python identifier,
    to element.
    '''
    pass

class AssemblageBase(ElementBase):
  '''
  Extends ElementBase so may be used as an element of an element.
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

class ComponentBase(ElementBase):
  '''
  Extends ElementBase adding support for attribute access and associated 
  resource status querying.
  '''
  @abstractmethod
  def digest(self):
    '''
    Returns an object that can be persisted and compared that represents a
    digest of the state of a component's associated resource(s).
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
  @abstractmethod
  def elementAttribute(self, id, name, default=AttributeError):
    '''
    Should return the value of the named attribute of the component's element
    object given by id - the type of id being dependent on the implementation
    of component (sub-)element collection. If the id is a valid identifier 
    for a component element and the string is the name of one of the object’s
    attributes, the result should be the value of that attribute. If the
    element or  named attribute does not exist, then default should be
    returned if provided, otherwise a LookupError (IndexError or KeyError
    as appropriate) or AttributeError should be raised.
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
    is returned. Otherwise, the digests compare equal and False is returned.
    Digest values should be associated with the str value of the element
    parameter.
    '''
    pass
  @abstractmethod
  def writeBack(self):
    '''
    Write back to any associated digest store the values of dirty (i.e. updated)
    element digests. If successfully written back then the digests should no
    longer be considered dirty.
    '''
    pass

class DigestStoreBase(metaclass=ABCMeta):
  '''
  Digest stores are intended to store digests of elements' associated
  resources to, usually, persistent storage. They allow single digests to be
  looked up by a key name - intended to be the str value of the element
  associated with the digest value and to update (or add) a set of new and
  changed element digest values.
  '''
  @abstractmethod
  def update(self, nameDigestPairs):
    '''
    The nameDigestPairs parameter should be a sequence of 
    (key name string, digest) pair sequences (e.g. tuples). It is intended
    that digest record for each key name is looked up in the store and if
    found replaced with the digest value of the (key name,digest) pair.
    Otherwise a new record is added to the store.
    '''
    pass
  @abstractmethod
  def retrieveDigest(self, recordName):
    '''
    The recordName parameter is intended to be a key name string, commonly a
    the str value of an assemblage element, for the required digest value to 
    retrieve and return. If not found a value convertible to False such as
    None should be returned
    '''
    pass

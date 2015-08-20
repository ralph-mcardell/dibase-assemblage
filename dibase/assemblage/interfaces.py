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

class ApplicatorBase(metaclass=ABCMeta):
  '''
  Defines methods for objects supporting the application of actions.
  '''
  @abstractmethod
  def apply(self, action):
    '''
    Applies action, generally a string that is a valid Python identifier,
    to element.
    '''
    pass
  @abstractmethod
  def _applyInner(self, action, resolver):
    '''
    Inner method used to apply function - not intended to be called by
    application code which should call apply. The _applyInner method is
    intended to be called on elements recursively initially from an application
    apply method call to perform the task of applying actions in the required
    manner. In addition to the outer application apply method's action string
    parameter _applyInner is also passed an action function (or method) resolver
    object that can be used to resolve action methods.
    '''
    pass

class ElementBase(ApplicatorBase):
  '''
  Defines methods required by users of objects representing assemblage elements
  (the assemblage.Assemblage and assemblage.Component classes for example)
  '''
  @abstractmethod
  def queryBeforeElementsActionsDone(self):
    '''
    Return true if component processed actions before processing (sub-)
    element components. Returns false otherwise.
    '''
    pass
  @abstractmethod
  def queryAfterElementsActionsDone(self):
    '''
    Return true if component processed actions after processing (sub-)
    element components. Returns false otherwise.
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
  '''
  Defines methods that are expected in an assemblage plan that can be used to
  construct an assemblage object.
  '''
  @abstractmethod
  def attributes(self):
    '''
    Returns an attributes map object that is used as an assemblage's assemblage
    scope attributes - including '__logger__', '__store__', and 
    '__resolution_plan__' for the logger, digestCache store, and action function
    resolver plan object used to create action function resolvers.
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

class CompoundBase(ApplicatorBase):
  '''
  Compounds are collections of component elements assumed to adhere to
  the ComponentBase base and implements ApplicatorBase to allow providing action
  application to contained components. Extended interface methods provide for
  querying action application state allowing using code to discover if any or
  all actions occurred before or after contained element processing.
  '''
  @abstractmethod
  def queryAnyBeforeElementsActionsDone(self):
    '''
    Return true if any elements processed actions before processing their (sub-)
    element components. Returns false otherwise.
    '''
    pass
  @abstractmethod
  def queryAllBeforeElementsActionsDone(self):
    '''
    Return true if all elements processed actions before processing their (sub-)
    element components. Returns false otherwise.
    '''
    pass
  @abstractmethod
  def queryAnyAfterElementsActionsDone(self):
    '''
    Return true if any elements processed actions after processing their (sub-)
    element components. Returns false otherwise.
    '''
    pass
  @abstractmethod
  def queryAllAfterElementsActionsDone(self):
    '''
    Return true if all elements processed actions after processing their (sub-)
    element components. Returns false otherwise.
    '''
    pass

class ResolverFactoryBase(metaclass=ABCMeta):
  '''
  ResolverFactory types create (function name) Resolver type instances.
  '''
  @abstractmethod
  def create(self, actionName, **dynamicInitArgs):
    '''
    Creates and returns an action function (or method) Resolver type instance.
    The actionName and dynamicInitArgs are typically passed to the resolver
    creation initialisation. 
    '''
    pass
  
class ResolverBase(metaclass=ABCMeta):
  '''
  Resolver types search for a action functions or methods and if successful
  return a callable object.
  '''
  @abstractmethod
  def resolve(self, fnName, object=None):
    '''
    Searches for a function or method indicated by fnName. The object parameter
    may be used as part of the search or just as a parameter that is passed to
    a resolved function or method. Note that the returned callable object should
    be callable with no parameters - in which case a call passing object can be
    wrapped in a lambda function expression. In the case that no function can be
    located the None should be returned.
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

#! /usr/bin/python3
# v3.4+
"""
Run all per-module quick but not-all-are-quite-unit-tests.
"""
import unittest
import inspect

if __name__ == '__main__':
  test_info = [ ('assemblage-Assemblage-tests', 'TestAssemblageAssemblage')
              , ('assemblage-Blueprint-tests', 'TestAssemblageBlueprint')
              , ('assemblage-Component-tests', 'TestAssemblageComponent')
              , ('assemblage-Compound-tests', 'TestAssemblageCompound')
              , ('assemblage-DigestCache-tests', 'TestAssemblageDigestCache')
              , ('assemblage-ShelfDigestStore-tests', 'TestAssemblageDigestStore')
              , ('assemblage-FileComponent-tests', 'TestAssemblageFileComponent')
              , ('assemblage-CompositeResolver-tests', 'TestAssemblageCompositeResolver')
              , ('assemblage-ResolverFactory-tests', 'TestAssemblageResolverFactory')
              , ('assemblage-ResolutionPlan-tests', 'TestAssemblageResolutionPlan')
              , ('assemblage-ObjectResolver-tests', 'TestAssemblageObjectResolver')
              , ('assemblage-CallFrameScopeResolver-tests', 'TestAssemblageCallFrameScopeResolver')
              ]
  ldr = unittest.TestLoader()
  test_suites = []
  for t in test_info:
    classes = inspect.getmembers( __import__(t[0])
                                , lambda obj : inspect.isclass(obj) and obj.__name__ == t[1]
                                )
    test_suites.append(ldr.loadTestsFromTestCase(classes[0][1]))
  all_tests = unittest.TestSuite(test_suites)
  unittest.TextTestRunner().run(all_tests.run)

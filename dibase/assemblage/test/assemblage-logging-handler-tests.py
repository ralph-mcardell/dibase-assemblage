#! /usr/bin/python3
# v3.4+
"""
Tests for dibase.assemblage.logging.handler configureObject tests 
"""
import unittest

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
from dibase.assemblage.logging import handler 
from dibase.assemblage.logging import OUTPUT 
from logging import INFO 
from logging import WARNING 
from logging import ERROR 
from logging import CRITICAL 
from logging import LogRecord  

#from dibase.assemblage.logging import Allow
#from dibase.assemblage.logging import Deny
#from dibase.assemblage.logging import configureLogger
#from dibase.assemblage.logging import addHandler
#from dibase.assemblage.logging import specifyLoggedLevels
#from dibase.assemblage.logging import logLevelsFor
#from dibase.assemblage.logging import setFormatter

class Record:
  def __init__(self, level, args=[]):
    self.levelno = level
    self.args = args
def makeLogRecord(msg, level):
  return LogRecord(name="testLogger", level=level, pathname="/this/file",lineno=111,msg=msg,args=[],exc_info=None)

class TestAssemblageLoggingKnownHandlers(unittest.TestCase):
  def test_000_known_handlers_are_initialised_as_expected_by_handler_initHandler(self):
    message = "this is the message"
    self.assertIsNone(handler.stdout)
    self.assertIsNone(handler.stderr)
    handler._initHandlers()
    self.assertIsNotNone(handler.stdout)
    self.assertIsNotNone(handler.stderr)
    self.assertFalse(handler.stdout.filter(Record(OUTPUT-1)))
    self.assertTrue(handler.stdout.filter(Record(OUTPUT)))
    self.assertFalse(handler.stdout.filter(Record(OUTPUT+1)))
    self.assertTrue(handler.stdout.handle(makeLogRecord(message,OUTPUT)))
    self.assertFalse(handler.stderr.filter(Record(INFO-1)))
    self.assertTrue(handler.stderr.filter(Record(INFO)))
    self.assertTrue(handler.stderr.filter(Record(WARNING)))
    self.assertTrue(handler.stderr.filter(Record(ERROR)))
    self.assertTrue(handler.stderr.filter(Record(CRITICAL)))
    self.assertFalse(handler.stderr.filter(Record(CRITICAL+1)))
    self.assertTrue(handler.stderr.handle(makeLogRecord(message,WARNING)))

if __name__ == '__main__':
  unittest.main()

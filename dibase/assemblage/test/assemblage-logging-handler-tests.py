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
from dibase.assemblage.logging import Allow
from dibase.assemblage.logging import Deny
from dibase.assemblage.logging import specifyLoggedLevels
from dibase.assemblage.logging import logLevelsFor
from logging import INFO
from logging import WARNING
from logging import ERROR
from logging import CRITICAL 
from logging import LogRecord
from logging import getLevelName
from logging import Formatter
from io import StringIO

class Record:
  def __init__(self, level, args=[]):
    self.levelno = level
    self.args = args
def makeLogRecord(msg, level):
  return LogRecord(name="testLogger", level=level, pathname="/this/file",lineno=111,msg=msg,args=[],exc_info=None)

def removeStdoutFilter():
  handler.stdout.removeFilter(handler.stdoutFilter)
  handler.stdoutFilter = None
def removeStderrFilter():
  handler.stderr.removeFilter(handler.stderrFilter)
  handler.stderrFilter = None
def resetStdoutFilter():
  if not handler.stdoutFilter:
    fn = specifyLoggedLevels(logLevelsFor(None, Allow(lambda lvl:lvl==OUTPUT)))
    fn(handler.stdout)
    handler.stdoutFilter = fn.filter
def resetStderrFilter():
  if not handler.stderrFilter:
    fn = specifyLoggedLevels(logLevelsFor(None, Allow(lambda lvl:lvl>=logging.INFO and lvl<=logging.CRITICAL)))
    fn(handler.stderr)
    handler.stderrFilter = fn.filter

class TestAssemblageLoggingKnownHandlers(unittest.TestCase):
  sstrmOut = StringIO()
  sstrmErr = StringIO()

  def test_000_known_handlers_are_initialised_as_expected_by_handler_initHandler(self):
# *MUST* be first test as it performs required one-time initialisation under test
#    print ("test_000_known_handlers_are_initialised_as_expected_by_handler_initHandler")
    message = "this is the message"
    self.assertIsNone(handler.stdout)
    self.assertIsNone(handler.stderr)
    sstrmOut = self.sstrmOut
    sstrmErr = self.sstrmErr
    
    old_stdout = sys.stdout
    sys.stdout = sstrmOut
    old_stderr = sys.stdout
    sys.stderr = sstrmErr 
    handler._initHandlers()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if len(sstrmOut.getvalue()) or len(sstrmErr.getvalue()):
      print("---------------------------------------------------------------------")
      print("Initialisation stdout output:\n%s"%sstrmOut.getvalue())
      print("Initialisation stderr output:\n%s"%sstrmErr.getvalue())
      print("---------------------------------------------------------------------")
    sstrmOut.truncate(0)
    sstrmOut.seek(0)
    sstrmErr.truncate(0)
    sstrmErr.seek(0)

    self.assertIsNotNone(handler.stdout)
    self.assertIsNotNone(handler.stderr)
    self.assertFalse(handler.stdout.filter(Record(OUTPUT-1)))
    self.assertTrue(handler.stdout.filter(Record(OUTPUT)))
    self.assertFalse(handler.stdout.filter(Record(OUTPUT+1)))
    self.assertTrue(handler.stdout.handle(makeLogRecord(message,OUTPUT)))
    self.assertEqual(sstrmOut.getvalue(), "%s\n"%message)
    self.assertFalse(handler.stderr.filter(Record(INFO-1)))
    self.assertTrue(handler.stderr.filter(Record(INFO)))
    self.assertTrue(handler.stderr.filter(Record(WARNING)))
    self.assertTrue(handler.stderr.filter(Record(ERROR)))
    self.assertTrue(handler.stderr.filter(Record(CRITICAL)))
    self.assertFalse(handler.stderr.filter(Record(CRITICAL+1)))
    self.assertTrue(handler.stderr.handle(makeLogRecord(message,WARNING)))
    self.assertRegex(sstrmErr.getvalue(), "^%s.*%s$"%(getLevelName(WARNING),message))
  def test_known_handler_can_have_allowed_logged_levels_denied_post_initialisation(self):
#    print ("test_known_handler_can_have_allowed_logged_levels_denied_post_initialisation")
    self.assertIsNotNone(handler.stdout)
    
    self.assertIsNotNone(handler.stdoutFilter)
  # adding a filter allows more logged messages to be denied ONLY
    fn = specifyLoggedLevels(logLevelsFor(None, Deny(lambda lvl:lvl==OUTPUT)))
    fn(handler.stdout)
    self.assertFalse(handler.stdout.filter(Record(OUTPUT-1)))
    self.assertFalse(handler.stdout.filter(Record(OUTPUT)))
    self.assertFalse(handler.stdout.filter(Record(OUTPUT+1)))
    handler.stdout.removeFilter(fn.filter)
  def test_known_handler_can_have_logged_levels_replaced_post_initialisation(self):
#    print ("test_known_handler_can_have_logged_levels_replaced_post_initialisation")
    self.assertIsNotNone(handler.stdout)
    self.assertIsNotNone(handler.stdoutFilter)
  # have to remove existing filter to allow previously denied messages to be logged
    removeStdoutFilter()
    fn = specifyLoggedLevels(logLevelsFor(None, Allow(lambda lvl:lvl==OUTPUT), Allow(lambda lvl:lvl==WARNING)))
    fn(handler.stdout)
    self.assertFalse(handler.stdout.filter(Record(OUTPUT-1)))
    self.assertTrue(handler.stdout.filter(Record(OUTPUT)))
    self.assertFalse(handler.stdout.filter(Record(OUTPUT+1)))
    self.assertFalse(handler.stdout.filter(Record(WARNING-1)))
    self.assertTrue(handler.stdout.filter(Record(WARNING)))
    self.assertFalse(handler.stdout.filter(Record(WARNING+1)))
    handler.stdout.removeFilter(fn.filter)
    resetStdoutFilter()
  def test_known_handler_can_have_formatter_replaced_post_initialisation(self):
#    print ("test_known_handler_can_have_formatter_replaced_post_initialisation")
    message = "this is the message"
    self.assertIsNotNone(handler.stdout)
    self.assertIsNotNone(handler.stdoutFilter)
    self.assertIsNotNone(handler.stdoutFormatter)
    msgPrefix = ">> "
    fmt = ''.join([msgPrefix,'%(message)s'])
    expectedLoggedText = ''.join([msgPrefix,message,'\n'])
    originalFormatter = handler.stdoutFormatter
    handler.stdout.setFormatter(Formatter(fmt))
    self.sstrmOut.truncate(0)
    self.sstrmOut.seek(0)

    self.assertTrue(handler.stdout.handle(makeLogRecord(message,OUTPUT)))
    self.assertEqual(self.sstrmOut.getvalue(), expectedLoggedText)

    handler.stdout.setFormatter(originalFormatter)
    handler.stdoutFormatter = originalFormatter

if __name__ == '__main__':
  unittest.main()

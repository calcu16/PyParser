#!/usr/bin/env python
# Copyright (c) 2013, Andrew Carter
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.

import unittest
from pyparser import Grammar, parse
from functools import partial
from pyparser.match import LastMatch

grammar = Grammar()
suites  = {}

class TestBase(unittest.TestCase):
  def setUp(self):
    pass
  def runParse(self, input, start, rest, expected):
    global grammar
    result = parse(grammar[start], input, LastMatch())
    if rest is None and result is None:
      self.assertIsNone(result)
    else:
      self.assertIsNotNone(result)
      pmatch, remainder = result
      self.assertEqual(pmatch.result, expected)
      self.assertEqual(list(remainder), list("" if rest is None else rest))
  def addParseTest(name, input, rest=None, result=None):
    setattr(TestBase, "test_parse_" + name, lambda self : self.runParse(input=input, start=name[:-1], rest=rest, expected=result))
  def loadParseTests(tests):
    for test in tests:
      TestBase.addParseTest(**test)
      suite = test["name"].split("_",1)[0]
      if suite not in suites:
        suites[suite] = unittest.TestSuite()
      suites[suite].addTest(TestBase('test_parse_' + test["name"]))

import test_basic
test_basic.addTests(grammar, TestBase)

if __name__ == '__main__':
  unittest.main()

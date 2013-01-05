#!/usr/bin/env python
# Copyright (c) 2012, Andrew Carter
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

from pyparser.base import Grammar, Any, Fail, Pattern, Save, Sequence
import unittest

grammar = Grammar()
grammar["any0"]        = Any()
grammar["any1"]        = Any(count=2)
grammar["cont0"]       = Fail(value=None)
grammar["cont1"]       = Fail(value=1)
grammar["pattern0"]    = Pattern("")
grammar["pattern1"]    = Pattern("abc")
grammar["save0"]       = Save(Any(), "save")
grammar["save1"]       = Save(Any(count=2), "save")
grammar["save2"]       = Save(Save(Any(), "save"), "save")
grammar["save3"]       = Save(Pattern("abc"),"save")
grammar["sequence0"]   = Sequence(children=[Any(),Any()])

class TestBase(unittest.TestCase):
  def setUp(self):
    pass
  def runTest(self, input, start, rest, value):
    global grammar
    result = grammar[start] << input
    if rest is None or result is None:
      self.assertEqual(rest, result)
    else:
      actual, remainder = result
      self.assertEqual(actual, value)
      self.assertEqual(list(remainder), list(rest))
  def addTest(name, input, start, rest, value):
    setattr(TestBase, "test_" + name, lambda self : self.runTest(input, start, rest, value))

tests  = (
  {
    "name"  : "any_00",
    "input" : "",
    "start" : "any0",
    "rest"  : None,
    "value" : {}
  },
  {
    "name"  : "any_01",
    "input" : "a",
    "start" : "any0",
    "rest"  : "",
    "value" : {}
  },
  {
    "name"  : "any_02",
    "input" : "ab",
    "start" : "any0",
    "rest"  : "b",
    "value" : {}
  },
  {
    "name"  : "any_03",
    "input" : "ab",
    "start" : "any1",
    "rest"  : "",
    "value" : {}
  },
  {
    "name"  : "cont_00",
    "input" : "",
    "start" : "cont0",
    "rest"  : None,
    "value" : None
  },
  {
    "name"  : "cont_01",
    "input" : "",
    "start" : "cont1",
    "rest"  : "",
    "value" : {}
  },
  {
    "name"  : "pattern_00",
    "input" : "",
    "start" : "pattern0",
    "rest"  : "",
    "value" : {}
  },
  {
    "name"  : "pattern_01",
    "input" : "abc",
    "start" : "pattern0",
    "rest"  : "abc",
    "value" : {}
  },
  {
    "name"  : "pattern_02",
    "input" : "abc",
    "start" : "pattern1",
    "rest"  : "",
    "value" : {}
  },
  {
    "name"  : "pattern_03",
    "input" : "abcdef",
    "start" : "pattern1",
    "rest"  : "def",
    "value" : {}
  },
  {
    "name"  : "save_00",
    "input" : "ab",
    "start" : "save0",
    "rest"  : "b",
    "value" : {"save":("a",)}
  },
  {
    "name"  : "save_01",
    "input" : "",
    "start" : "save0",
    "rest"  : None,
    "value" : None
  },
  {
    "name"  : "save_02",
    "input" : "abc",
    "start" : "save1",
    "rest"  : "c",
    "value" : {"save":("a","b")}
  },
  {
    "name"  : "save_03",
    "input" : "ab",
    "start" : "save2",
    "rest"  : "b",
    "value" : {"save":{"save":("a",)}}
  },
  {
    "name"  : "save_04",
    "input" : "abc",
    "start" : "save3",
    "rest"  : "",
    "value" : {"save":("a","b","c")}
  },
  {
    "name"  : "sequence_00",
    "input" : "abc",
    "start" : "sequence0",
    "rest"  : "c",
    "value" : {}
  },
)

for test in tests:
  TestBase.addTest(**test)

if __name__ == '__main__':
  unittest.main()

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

from pyparser import Grammar, Any, Fail, Pattern, parse
from pyparser import re as re2
import unittest

match  = { "name" : "match" , "pre" : re2.Match.child, "post" : re2.Match.parent }
match2 = { "name" : "match2", "pre" : re2.Match.child, "post" : re2.Match.parent }

grammar = Grammar()
grammar["any0"]        = Any()
grammar["any1"]        = Any(count=2)
grammar["choice0"]     = (Pattern("a") | Pattern("b"))(**match)
grammar["choice1"]     = Fail(value=1) & Any()(**match) & Any() \
                       | Fail(value=2) & Any() & Any()(**match)
grammar["choice2"]     = Fail(value=2) & Any()(**match) & Any() \
                       | Fail(value=1) & Any() & Any()(**match)
grammar["choice3"]     = Any()(**match) & Any() & Fail(value=1) \
                       | Any() & Any()(**match) & Fail(value=2)
grammar["choice4"]     = Any()(**match) & Any() & Fail(value=2) \
                       | Any() & Any()(**match) & Fail(value=1)
grammar["choice5"]     = (Pattern("a") | Pattern("b")(**match)) & Any()(**match)
grammar["cont0"]       = Fail(value=None)
grammar["cont1"]       = Fail(value=1)
grammar["match0"]      = Any()(**match)
grammar["match1"]      = (Any(count=2))(**match)
grammar["match2"]      = (Any())(**match)(**match)
grammar["match3"]      = (Any())(**match)(**match2)
grammar["match4"]      = (Pattern("abc"))(**match)
grammar["pattern0"]    = Pattern("")
grammar["pattern1"]    = Pattern("abc")
grammar["sequence0"]   = Any() & Any()
grammar["sequence1"]   = (Any())(**match) & Any()
grammar["sequence2"]   = Any() & (Any())(**match)
grammar["sequence3"]   = Any() & (Any())(**match) & Fail(value=1)
grammar["sequence4"]   = (Any())(**match) & (Any())(**match2)

class TestBase(unittest.TestCase):
  def setUp(self):
    pass
  def runTest(self, input, start, rest, groups, groupd):
    global grammar
    result = parse(grammar[start], input, re2.Match())
    if rest is None and groups is None and groupd is None:
      self.assertIsNone(result)
    else:
      self.assertIsNotNone(result)
      pmatch, remainder = result
      self.assertEqual(pmatch.groups(), () if groups is None else groups)
      self.assertEqual(pmatch.groupdict(), {} if groupd is None else groupd)
      self.assertEqual(list(remainder), list("" if rest is None else rest))
  def addTest(name, input, start, rest=None, groups=None, groupd=None):
    setattr(TestBase, "test_" + name, lambda self : self.runTest(input, start, rest, groups, groupd))

tests  = (
  {
    "name"  : "any_00",
    "input" : "",
    "start" : "any0",
    
  },
  {
    "name"  : "any_01",
    "input" : "a",
    "start" : "any0",
    "rest"  : "",
  },
  {
    "name"  : "any_02",
    "input" : "ab",
    "start" : "any0",
    "rest"  : "b",
  },
  {
    "name"  : "any_03",
    "input" : "ab",
    "start" : "any1",
    "rest"  : "",
  },
  {
    "name"  : "choice_00",
    "input" : "ac",
    "start" : "choice0",
    "rest"  : "c",
    "groups": ("a",),
    "groupd": {"match":"a"}
   },
  {
    "name"  : "choice_01",
    "input" : "bc",
    "start" : "choice0",
    "rest"  : "c",
    "groups": ("b",),
    "groupd": {"match":"b"}
  },
  {
    "name"  : "choice_02",
    "input" : "c",
    "start" : "choice0",
  },
  {
    "name"  : "choice_03",
    "input" : "abc",
    "start" : "choice1",
    "rest"  : "c",
    "groups": ("a",None),
    "groupd": {"match":"a"}
  },
  {
    "name"  : "choice_04",
    "input" : "c",
    "start" : "choice1",
  },
  {
    "name"  : "choice_05",
    "input" : "abc",
    "start" : "choice2",
    "rest"  : "c",
    "groups": (None,"b"),
    "groupd": {"match":"b"}
  },
  {
    "name"  : "choice_06",
    "input" : "c",
    "start" : "choice2",
  },
  {
    "name"  : "choice_07",
    "input" : "abc",
    "start" : "choice3",
    "rest"  : "c",
    "groups": ("a",None),
    "groupd": {"match":"a"}
  },
  {
    "name"  : "choice_08",
    "input" : "c",
    "start" : "choice3",
  },
  {
    "name"  : "choice_09",
    "input" : "abc",
    "start" : "choice4",
    "rest"  : "c",
    "groups": (None,"b"),
    "groupd": {"match":"b"}
  },
  {
    "name"  : "choice_10",
    "input" : "c",
    "start" : "choice4",
  },
  {
    "name"  : "choice_11",
    "input" : "ac",
    "start" : "choice5",
    "rest"  : "",
    "groups": (None,"c"),
    "groupd": {"match":"c"}
  },
  {
    "name"  : "cont_00",
    "input" : "",
    "start" : "cont0",
  },
  {
    "name"  : "cont_01",
    "input" : "",
    "start" : "cont1",
    "rest"  : "",
  },
  {
    "name"  : "match_00",
    "input" : "ab",
    "start" : "match0",
    "rest"  : "b",
    "groups": ("a",),
    "groupd": {"match":"a"}
  },
  {
    "name"  : "match_01",
    "input" : "",
    "start" : "match0",
  },
  {
    "name"  : "match_02",
    "input" : "abc",
    "start" : "match1",
    "rest"  : "c",
    "groups": ("ab",),
    "groupd": {"match":"ab"}
  },
  {
    "name"  : "match_03",
    "input" : "ab",
    "start" : "match2",
    "rest"  : "b",
    "groups": ("a","a"),
    "groupd": {"match":"a"}
  },
  {
    "name"  : "match_04",
    "input" : "ab",
    "start" : "match3",
    "rest"  : "b",
    "groups": ("a","a"),
    "groupd": {"match":"a","match2":"a"}
  },
  {
    "name"  : "match_05",
    "input" : "abc",
    "start" : "match4",
    "rest"  : "",
    "groups": ("abc",),
    "groupd": {"match":"abc"}
  },
  {
    "name"  : "pattern_00",
    "input" : "",
    "start" : "pattern0",
    "rest"  : "",
  },
  {
    "name"  : "pattern_01",
    "input" : "abc",
    "start" : "pattern0",
    "rest"  : "abc",
  },
  {
    "name"  : "pattern_02",
    "input" : "abc",
    "start" : "pattern1",
    "rest"  : "",
  },
  {
    "name"  : "pattern_03",
    "input" : "abcdef",
    "start" : "pattern1",
    "rest"  : "def",
  },
  {
    "name"  : "sequence_00",
    "input" : "abc",
    "start" : "sequence0",
    "rest"  : "c",
  },
  {
    "name"  : "sequence_01",
    "input" : "",
    "start" : "sequence0",
  },
  {
    "name"  : "sequence_02",
    "input" : "abc",
    "start" : "sequence1",
    "rest"  : "c",
    "groups": ("a",),
    "groupd": {"match":"a"}
  },
  {
    "name"  : "sequence_03",
    "input" : "",
    "start" : "sequence1",
  },
  {
    "name"  : "sequence_04",
    "input" : "abc",
    "start" : "sequence2",
    "rest"  : "c",
    "groups": ("b",),
    "groupd": {"match":"b"}
  },
  {
    "name"  : "sequence_05",
    "input" : "",
    "start" : "sequence2",
  },
  {
    "name"  : "sequence_06",
    "input" : "abc",
    "start" : "sequence3",
    "rest"  : "c",
    "groups": ("b",),
    "groupd": {"match":"b"}
  },
  {
    "name"  : "sequence_07",
    "input" : "",
    "start" : "sequence3",
  },
  {
    "name"  : "sequence_08",
    "input" : "ab",
    "start" : "sequence4",
    "rest"  : "",
    "groups": ("a","b"),
    "groupd": {"match":"a","match2":"b"}
  },
  {
    "name"  : "sequence_09",
    "input" : "abc",
    "start" : "sequence4",
    "rest"  : "c",
    "groups": ("a","b"),
    "groupd": {"match":"a","match2":"b"}
  },
  {
    "name"  : "sequence_10",
    "input" : "a",
    "start" : "sequence3",
  },
)

for test in tests:
  TestBase.addTest(**test)

if __name__ == '__main__':
  unittest.main()

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

from pyparser import Grammar, Any, Pattern # , Fail, Pattern
import unittest

grammar = Grammar()
grammar["any0"]        = Any()
grammar["any1"]        = Any(count=2)
'''
grammar["choice0"]     = (Pattern("a") | Pattern("b"))("save")
grammar["choice1"]     = Fail(value=1) & Any()("save") & Any() \
                       | Fail(value=2) & Any() & Any()("save")
grammar["choice2"]     = Fail(value=2) & Any()("save") & Any() \
                       | Fail(value=1) & Any() & Any()("save")
grammar["choice3"]     = Any()("save") & Any() & Fail(value=1) \
                       | Any() & Any()("save") & Fail(value=2)
grammar["choice4"]     = Any()("save") & Any() & Fail(value=2) \
                       | Any() & Any()("save") & Fail(value=1)
grammar["cont0"]       = Fail(value=None)
grammar["cont1"]       = Fail(value=1)
'''
grammar["pattern0"]    = Pattern("")
grammar["pattern1"]    = Pattern("abc")
grammar["save0"]       = Any()("save")
grammar["save1"]       = (Any(count=2))("save")
grammar["save2"]       = (Any())("save")("save")
grammar["save3"]       = (Any())("save")("save2")
grammar["save4"]       = (Pattern("abc"))("save")

'''
grammar["sequence0"]   = Any() & Any()
grammar["sequence1"]   = (Any())("save") & Any()
grammar["sequence2"]   = Any() & (Any())("save")
grammar["sequence3"]   = Any() & (Any())("save") & Fail(value=1)
grammar["sequence4"]   = (Any())("save0") & (Any())("save1")
'''

class TestBase(unittest.TestCase):
  def setUp(self):
    pass
  def runTest(self, input, start, rest, groups, groupd):
    global grammar
    result = grammar[start] << input
    if rest is None and groups is None and groupd is None:
      self.assertIsNone(result)
    else:
      self.assertIsNotNone(result)
      pmatch, remainder = result
      if groups is not None:
        self.assertEqual(pmatch.groups(), groups)
      if groupd is not None:
        self.assertEqual(pmatch.groupdict(), groupd)
      if rest is not None:
        self.assertEqual(list(remainder), list(rest))
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
  # {
    # "name"  : "choice_00",
    # "input" : "ac",
    # "start" : "choice0",
    # "rest"  : "c",
    # "groups" : {"save":"a"}
  # },
  # {
    # "name"  : "choice_01",
    # "input" : "bc",
    # "start" : "choice0",
    # "rest"  : "c",
    # "groups" : {"save":"b"}
  # },
  # {
    # "name"  : "choice_02",
    # "input" : "c",
    # "start" : "choice0",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "choice_03",
    # "input" : "abc",
    # "start" : "choice1",
    # "rest"  : "c",
    # "groups" : {"save":"a"}
  # },
  # {
    # "name"  : "choice_04",
    # "input" : "c",
    # "start" : "choice1",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "choice_05",
    # "input" : "abc",
    # "start" : "choice2",
    # "rest"  : "c",
    # "groups" : {"save":"b"}
  # },
  # {
    # "name"  : "choice_06",
    # "input" : "c",
    # "start" : "choice2",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "choice_07",
    # "input" : "abc",
    # "start" : "choice3",
    # "rest"  : "c",
    # "groups" : {"save":"a"}
  # },
  # {
    # "name"  : "choice_08",
    # "input" : "c",
    # "start" : "choice3",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "choice_09",
    # "input" : "abc",
    # "start" : "choice4",
    # "rest"  : "c",
    # "groups" : {"save":"b"}
  # },
  # {
    # "name"  : "choice_10",
    # "input" : "c",
    # "start" : "choice4",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "cont_00",
    # "input" : "",
    # "start" : "cont0",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "cont_01",
    # "input" : "",
    # "start" : "cont1",
    # "rest"  : "",
    # "groups" : {}
  # },
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
    "name"  : "save_00",
    "input" : "ab",
    "start" : "save0",
    "rest"  : "b",
    "groups": ("a",),
    "groupd": {"save":"a"}
  },
  {
    "name"  : "save_01",
    "input" : "",
    "start" : "save0",
  },
  {
    "name"  : "save_02",
    "input" : "abc",
    "start" : "save1",
    "rest"  : "c",
    "groups" : ("ab",),
    "groupd": {"save":"ab"}
  },
  {
    "name"  : "save_03",
    "input" : "ab",
    "start" : "save2",
    "rest"  : "b",
    "groups" : ("a","a"),
    "groupd": {"save":"a"}
  },
  {
    "name"  : "save_04",
    "input" : "ab",
    "start" : "save3",
    "rest"  : "b",
    "groups" : ("a","a"),
    "groupd": {"save":"a","save2":"a"}
  },
  {
    "name"  : "save_05",
    "input" : "abc",
    "start" : "save4",
    "rest"  : "",
    "groups" : ("abc",),
    "groupd": {"save":"abc"}
  },
  # {
    # "name"  : "sequence_00",
    # "input" : "abc",
    # "start" : "sequence0",
    # "rest"  : "c",
    # "groups" : {}
  # },
  # {
    # "name"  : "sequence_01",
    # "input" : "",
    # "start" : "sequence0",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "sequence_02",
    # "input" : "abc",
    # "start" : "sequence1",
    # "rest"  : "c",
    # "groups" : {"save":"a"}
  # },
  # {
    # "name"  : "sequence_03",
    # "input" : "",
    # "start" : "sequence1",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "sequence_04",
    # "input" : "abc",
    # "start" : "sequence2",
    # "rest"  : "c",
    # "groups" : {"save":"b"}
  # },
  # {
    # "name"  : "sequence_05",
    # "input" : "",
    # "start" : "sequence2",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "sequence_06",
    # "input" : "abc",
    # "start" : "sequence3",
    # "rest"  : "c",
    # "groups" : {"save":"b"}
  # },
  # {
    # "name"  : "sequence_07",
    # "input" : "",
    # "start" : "sequence3",
    # "rest"  : None,
    # "groups" : None
  # },
  # {
    # "name"  : "sequence_08",
    # "input" : "ab",
    # "start" : "sequence4",
    # "rest"  : "",
    # "groups" : {"save0":"a","save1":"b"}
  # },
  # {
    # "name"  : "sequence_09",
    # "input" : "abc",
    # "start" : "sequence4",
    # "rest"  : "c",
    # "groups" : {"save0":"a","save1":"b"}
  # },
  # {
    # "name"  : "sequence_10",
    # "input" : "a",
    # "start" : "sequence3",
    # "rest"  : None,
    # "groups" : None
  # },
)

for test in tests:
  TestBase.addTest(**test)

if __name__ == '__main__':
  unittest.main()

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

import pyparser.base as base
import unittest

class TestBase(unittest.TestCase):
  def setUp(self):
    pass
  def runTest(self, lookup, input, start, rest):
    result = base.parse(start, lookup, input)
    if rest is None or result is None:
      self.assertEqual(rest, result)
    else:
      match, remainder = result
      self.assertEqual(list(remainder), list(rest))
  def addTest(name, lookup, input, start, rest):
    setattr(TestBase, "test_" + name, lambda self : self.runTest(lookup, input, start, rest))

lookup = {
  "A" : base.Pattern("abc"),
  "B" : base.Pattern("abc") | base.Pattern("def"),
  "C" : base.Pattern("ab")  & base.Pattern("c"),
  "D" : base.Lookup("A"),
  "E" : +base.Lookup("A"),
  "F" : base.Pattern("ab")  & base.Pattern("c") | base.Pattern("abd"),
  "G" : base.Lookup("A") | base.Pattern("def"),
  "H" : base.Pattern("def") | base.Lookup("A"),
  "I" : base.Lookup("C") | base.Pattern("def"),
  "J" : base.Pattern("abc") & base.eof,
}

expression = {
  "line"  : base.Lookup("expr") & base.eof,
  "expr"  : base.Lookup("atom"),
  "atom"  : base.Lookup("NUM")
          | base.Lookup("LPAREN") & base.Lookup("expr") & base.Lookup("RPAREN"),
  "LPAREN": base.Pattern("(") & base.Lookup("WS"),
  "RPAREN": base.Pattern(")") & base.Lookup("WS"),
  "NUM"   : base.Set("0123456789") & base.Repeat(base.Set("0123456789")) & base.Lookup("WS"),
  "WS"    : base.Repeat(base.Pattern(" ")),
}

tests  = (
  {
    "name"  : "any_00",
    "input" : "",
    "lookup": {"any": base.any},
    "start" : "any",
    "rest"  : None
  },
  {
    "name"  : "match_00",
    "input" : "abc",
    "lookup": lookup,
    "start" : "A",
    "rest"  : ""
  },
  {
    "name"  : "match_01",
    "input" : "abcd",
    "lookup": lookup,
    "start" : "A",
    "rest"  : "d"
  },
  {
    "name"  : "match_02",
    "input" : "ab",
    "lookup": lookup,
    "start" : "A",
    "rest"  : None
  },
  {
    "name"  : "sequence_00",
    "input" : "abc",
    "lookup": lookup,
    "start" : "C",
    "rest"  : ""
  },
  {
    "name"  : "sequence_01",
    "input" : "ab",
    "lookup": lookup,
    "start" : "C",
    "rest"  : None
  },
  {
    "name"  : "sequence_02",
    "input" : "c",
    "lookup": lookup,
    "start" : "C",
    "rest"  : None
  },
  {
    "name"  : "sequence_03",
    "input" : "abd",
    "lookup": lookup,
    "start" : "C",
    "rest"  : None
  },
  {
    "name"  : "sequence_04",
    "input" : "abc",
    "lookup": lookup,
    "start" : "F",
    "rest"  : ""
  },
  {
    "name"  : "sequence_05",
    "input" : "abd",
    "lookup": lookup,
    "start" : "F",
    "rest"  : ""
  },
  {
    "name"  : "sequence_06",
    "input" : "abe",
    "lookup": lookup,
    "start" : "F",
    "rest"  : None
  },
  {
    "name"  : "ordered_00",
    "input" : "abc",
    "lookup": lookup,
    "start" : "B",
    "rest"  : ""
    
  },
  {
    "name"  : "ordered_01",
    "input" : "def",
    "lookup": lookup,
    "start" : "B",
    "rest"  : ""
    
  },
  {
    "name"  : "lookup_00",
    "input" : "abc",
    "lookup": lookup,
    "start" : "D",
    "rest"  : ""
  },
  {
    "name"  : "lookup_01",
    "input" : "abc",
    "lookup": lookup,
    "start" : "G",
    "rest"  : ""
  },
  {
    "name"  : "lookup_02",
    "input" : "def",
    "lookup": lookup,
    "start" : "G",
    "rest"  : ""
  },
  {
    "name"  : "lookup_03",
    "input" : "abc",
    "lookup": lookup,
    "start" : "H",
    "rest"  : ""
  },
  {
    "name"  : "lookup_04",
    "input" : "def",
    "lookup": lookup,
    "start" : "H",
    "rest"  : ""
  },
  {
    "name"  : "lookup_05",
    "input" : "abc",
    "lookup": lookup,
    "start" : "I",
    "rest"  : ""
  },
  {
    "name"  : "lookup_06",
    "input" : "def",
    "lookup": lookup,
    "start" : "I",
    "rest"  : ""
  },
  {
    "name"  : "test_00",
    "input" : "abc",
    "lookup": lookup,
    "start" : "E",
    "rest"  : "abc"
  },
  {
    "name"  : "eof_00",
    "input" : "abc",
    "lookup": lookup,
    "start" : "J",
    "rest"  : ""
  },
  {
    "name"  : "eof_01",
    "input" : "abcd",
    "lookup": lookup,
    "start" : "J",
    "rest"  : None
  },
  {
    "name"  : "expr_00",
    "input" : "123",
    "lookup": expression,
    "start" : "expr",
    "rest"  : ""
  },
  {
    "name"  : "expr_01",
    "input" : "(123)",
    "lookup": expression,
    "start" : "line",
    "rest"  : ""
  },
)

for test in tests:
  TestBase.addTest(**test)

if __name__ == '__main__':
  unittest.main()

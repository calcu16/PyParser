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
import base
import unittest


class TestBase(unittest.TestCase):
  def setUp(self):
    pass
  def runTest(self, lookup, input, start, rest):
    remainder = base.parse(start, lookup, input)
    if remainder is not None: remainder = list(remainder)
    if rest is not None: rest = list(rest)
    self.assertEqual(remainder, rest)
  def addTest(name, lookup, input, start, rest):
    setattr(TestBase, "test_" + name, lambda self : self.runTest(lookup, input, start, rest))

lookup = {
  "A" : base.Match("abc"),
  "B" : base.Match("abc") | base.Match("def"),
  "C" : base.Match("ab")  & base.Match("c"),
  "D" : base.Lookup("A"),
}

tests  = (
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
    "name"  : "sequence",
    "input" : "abc",
    "lookup": lookup,
    "start" : "C",
    "rest"  : ""
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
  }
)

for test in tests:
  TestBase.addTest(**test)

if __name__ == '__main__':
  unittest.main()

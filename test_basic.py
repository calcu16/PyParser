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

from pyparser.combinator import Any, Fail, Pattern

tests = (
  {
    "name"  : "any_00",
    "input" : "",
    "rest"  : "",
    "result": ("",),
  },
  {
    "name"  : "any_00",
    "input" : "a",
    "rest"  : "a",
    "result": (),
  },
  {
    "name"  : "any_10",
    "input" : "",
  },
  {
    "name"  : "any_11",
    "input" : "a",
    "rest"  : "",
    "result": ("a",),
  },
  {
    "name"  : "any_12",
    "input" : "abc",
    "rest"  : "bc",
    "result": ("a",),
  },
  {
    "name"  : "choice_00",
    "input" : "acd",
    "rest"  : "cd",
    "result": ("a",),
  },
  {
    "name"  : "choice_01",
    "input" : "bcd",
    "rest"  : "cd",
    "result": ("b",),
  },
  {
    "name"  : "choice_02",
    "input" : "cc",
  },
  {
    "name"  : "choice_03",
    "input" : "",
  },
  {
    "name"  : "choice_10",
    "input" : "acd",
    "rest"  : "d",
    "result": ("c",),
  },
  {
    "name"  : "choice_11",
    "input" : "bcd",
    "rest"  : "d",
    "result": ("c",),
  },
  {
    "name"  : "choice_12",
    "input" : "cc",
  },
  {
    "name"  : "choice_13",
    "input" : "",
  },
  {
    "name"  : "choice_20",
    "input" : "acd",
    "rest"  : "d",
    "result": ("c",),
  },
  {
    "name"  : "choice_21",
    "input" : "ad",
    "rest"  : "d",
    "result": ("a",),
  },
  {
    "name"  : "choice_22",
    "input" : "c",
  },
  {
    "name"  : "choice_23",
    "input" : "",
  },
  {
    "name"  : "choice_30",
    "input" : "abd",
    "rest"  : "d",
    "result": ("b",),
  },
  {
    "name"  : "choice_31",
    "input" : "acd",
    "rest"  : "d",
    "result": ("c",),
  },
  {
    "name"  : "choice_32",
    "input" : "ad",
  },
  {
    "name"  : "choice_33",
    "input" : "",
  },
  
  {
    "name"  : "cont_00",
    "input" : "",
  },
  {
    "name"  : "cont_10",
    "input" : "",
    "rest"  : "",
  },
  {
    "name"  : "negative_00",
    "input" : "abc",
    "rest"  : "",
    "result": ("a","b","c",),
  },
  {
    "name"  : "negative_01",
    "input" : "abcd",
  },
  {
    "name"  : "pattern_00",
    "input" : "",
    "rest"  : "",
    "result": (),
  },
  {
    "name"  : "pattern_01",
    "input" : "abc",
    "rest"  : "abc",
    "result": (),
  },
  {
    "name"  : "pattern_10",
    "input" : "abc",
    "rest"  : "",
    "result": ("a","b","c",),
  },
  {
    "name"  : "pattern_11",
    "input" : "abcdef",
    "rest"  : "def",
    "result": ("a","b","c",),
  },
  {
    "name"  : "pattern_12",
    "input" : "",
  },
  {
    "name"  : "pattern_13",
    "input" : "def",
  },
  {
    "name"  : "sequence_00",
    "input" : "ab",
    "rest"  : "",
    "result": ("b",),
  },
  {
    "name"  : "sequence_01",
    "input" : "abc",
    "rest"  : "c",
    "result": ("b",),
  },
  {
    "name"  : "sequence_02",
    "input" : "",
  },
  {
    "name"  : "sequence_03",
    "input" : "a",
  },
  {
    "name"  : "sequence_10",
    "input" : "",
    "rest"  : "",
    "result": (),
  },
  {
    "name"  : "sequence_11",
    "input" : "a",
    "rest"  : "a",
    "result": (),
  },
  {
    "name"  : "sequence_20",
    "input" : "abc",
    "rest"  : "",
    "result": ("c",),
  },
  {
    "name"  : "sequence_21",
    "input" : "abcdef",
    "rest"  : "def",
    "result": ("c",),
  },
  {
    "name"  : "sequence_22",
    "input" : "",
  },
  {
    "name"  : "sequence_23",
    "input" : "ab",
  },
)

def addTests(grammar, testbase):
  grammar["any_0"]      = Any(count=0)
  grammar["any_1"]      = Any()
  grammar["any_2"]      = Any(count=2)
  grammar["choice_0"]   = Pattern("a") | Pattern("b")
  grammar["choice_1"]   = (Pattern("a") | Pattern("b")) & Pattern("c")
  grammar["choice_2"]   = Pattern("a") & Pattern("c") | Pattern("a")
  grammar["choice_3"]   = Fail(value=1) & Pattern("a") & Fail(value=2) & Pattern("b") | Fail(value=2) & Pattern("a") & Fail(value=1) & Pattern("c")
  grammar["cont_0"]     = Fail(value=None)
  grammar["cont_1"]     = Fail(value=1)
  grammar["negative_0"] = Pattern("abc") & -Any(count=1)
  grammar["pattern_0"]  = Pattern("")
  grammar["pattern_1"]  = Pattern("abc")
  grammar["sequence_0"] = Any() & Any()
  grammar["sequence_1"] = Any(count=0) & Any(count=0)
  grammar["sequence_2"] = Any() & Any() & Any()
  
  testbase.loadParseTests(tests)

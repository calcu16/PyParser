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

from pyparser.combinator import Any

tests = (
  {
    "name" : "yacc_any_10",
    "input": "",
  },
  {
    "name"  : "yacc_any_11",
    "input" : "a",
    "result": ("a",)
  },
  {
    "name"  : "yacc_sequence_00",
    "input" : "ab",
    "result": ("a",)
  },
  {
    "name"  : "yacc_sequence_10",
    "input" : "ab",
    "result": ("b",)
  },
  {
    "name"  : "yacc_sequence_20",
    "input" : "ab",
    "result": ("a",)
  },
)

def addTests(grammar, testbase):
  grammar["yacc_any_1"]      = Any() ^ (lambda a : a)
  grammar["yacc_sequence_0"] = Any() & Any() ^ (lambda a, b : a)
  grammar["yacc_sequence_1"] = Any() & Any() ^ (lambda a, b : b)
  grammar["yacc_sequence_2"] = (Any() ^ "f") & (Any() ^ "l") ^ (lambda **a : a["f"])
  return testbase.loadParseTests(tests, "yacc")

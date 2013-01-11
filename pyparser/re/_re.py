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

from .. import Grammar, Any, Pattern, parse, AbstractMatch

_regrammar = Grammar()

class EmptyMatch(AbstractMatch):
  def __init__(self, parent=None):
    self.parent = parent
  def pre (self, **kwargs):
    assert(False)
    return EmptyMatch(self)
  def post(self, **kwargs):
    self.parent += Any(count=0)
    return self.parent

class CharMatch(AbstractMatch):
  def __init__(self, parent=None):
    self.result = ""
    self.parent = parent
  def pre (self, **kwargs):
    return CharMatch(self)
  def post(self, **kwargs):
    self.parent += Pattern(self.result)
    return self.parent
  def __iadd__(self, rhs):
    assert(type(rhs) is not Any)
    self.result += "".join(rhs)
    return self

class SeqMatch(AbstractMatch):
  def __init__(self, parent=None):
    self.result = Any(count=0)
    self.parent = parent
  def pre (self, **kwargs):
    return SeqMatch(self)
  def post(self, **kwargs):
    self.parent += self.result
    return self.parent
  def __iadd__(self, rhs):
    self.result = self.result & rhs
    return self

class StartMatch(AbstractMatch):
  def __init__(self, parent=None):
    self.result = None
    self.parent = parent
  def __iadd__(self, rhs):
    self.result = rhs
    return self

regrammar = Grammar()
regrammar["empty"] = Any(count=0)(pre=CharMatch.pre,post=CharMatch.post)
regrammar["_char"] = Pattern("a") | Pattern("b") | Pattern("c") | Pattern("d")
regrammar[ "char"] = regrammar["_char"](pre=CharMatch.pre,post=CharMatch.post)
regrammar[ "atom"] = regrammar["char"]
regrammar["_seqz"] = regrammar["atom"] & regrammar["seqz"] | regrammar["empty"]
regrammar[ "seqz"] = regrammar["_seqz"](pre=SeqMatch.pre,post=SeqMatch.post)
regrammar["start"] = regrammar["seqz"] & -Any(count=1)

class _compiled(object):
  def __init__(self, match):
    self.grammar = Grammar()
    self.grammar["start"] = match[0].result
  def __str__(self):
    return str(~self.grammar["start"])

def compile(pattern):
  global regrammar
  match = parse(regrammar["start"], pattern, StartMatch())
  return _compiled(match)

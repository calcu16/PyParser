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

from .. import Grammar, Any, Charset, Pattern, parse
from .._match import BasicMatch

_regrammar = Grammar()

IgnoreMatch= BasicMatch(iadd=lambda lhs, rhs : None, consume=None)
PatMatch   = BasicMatch(iadd=lambda lhs, rhs : lhs + rhs,consume=lambda result : Pattern("".join(result)), result=())
SetMatch   = BasicMatch(iadd=lambda lhs, rhs : lhs + rhs,consume=lambda result : Charset(result), result=())
SeqMatch   = BasicMatch(iadd=lambda lhs, rhs : lhs & rhs,result=Any(count=0))
OptMatch   = BasicMatch(iadd=lambda lhs, rhs : lhs | rhs,result=-Any(count=0)) 
StartMatch = BasicMatch(iadd=lambda lhs, rhs : rhs      ,consume=None)


regrammar = Grammar()
regrammar["empty"] = Pattern("")                                          ^ (lambda _ : Pattern(""))
regrammar[ "char"] = -Charset(set=set('()[]|')) & Any(count=1)            ^ (lambda a : Pattern(a[0]))
regrammar[ "prec"] = Pattern("(?:") & regrammar["re"] & Pattern(")")      ^ (lambda l, re, r : re)
regrammar[ "atom"] = regrammar["char"] | regrammar["prec"]
regrammar[ "seqz"] = regrammar["atom"] & regrammar["seqz"]                ^ (lambda lhs, rhs : lhs & rhs) \
                   | regrammar["empty"]
regrammar[ "opts"] = regrammar["seqz"] & Pattern("|") & regrammar["opts"] ^ (lambda lhs, op, rhs : lhs | rhs) \
                   | regrammar["seqz"]
regrammar[   "re"] = regrammar["opts"]
regrammar["start"] = regrammar["re"] & -Any(count=1)

class _compiled(object):
  def __init__(self, match):
    self.grammar = Grammar()
    self.grammar["start"] = match[0].result
  def __str__(self):
    return str(~self.grammar["start"])

def compile(pattern):
  global regrammar
  match = parse(regrammar["start"], pattern, StartMatch.produce(None))
  return _compiled(match)

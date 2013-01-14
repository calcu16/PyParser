#!/usr/bin/env python
# Copyright (c) 2013, Andrew Carter
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
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
from .combinator._debug import assertSucc, assertFail
from .combinator import Lookup
from ._util import fork, tailEval
from functools import partial

@assertSucc
def _SUCC(pmatch, input, **kwargs):
  return pmatch, input

@assertFail
def _FAIL(value, cont, **kwargs):
  if value is None:
    return None
  else:
    return partial(cont,fail=_FAIL)

def parse(pobj, input, pmatch=None):
  global _SUCC, _FAIL, fork
  parseArgs = {
    'input'     : fork(input),
    'succ'      : _SUCC,
    'fail'      : _FAIL,
    'pmatch'    : pmatch,
  }
  return tailEval(pobj.parse(**parseArgs))

class Grammar(object):
  def __init__(self, *args, **kwargs):
    self.children = args
    self.lookup   = kwargs
  def __setitem__(self, name, item):
    self.lookup[name] = item
    item.grammar = self
  def __getitem__(self, name):
    return Lookup(name=name, grammar=self)


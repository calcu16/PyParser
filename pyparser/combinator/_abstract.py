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

from ._debug import assertParse, badcall
from functools import partial

def DIE(fail, **kwargs):
  return partial(fail,value=None,cont=badcall)

class AbstractCombinator(object):
  def __init__(self, grammar=None, children=(), prec=0, sep=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    super().__setattr__('grammar',None)
    self.children = tuple(children)
    for child in children: assert(child is not None)
    self.grammar = grammar
    self.prec = prec
    self.sep  = None
  def __setattr__(self, name, value):
    update = False
    if name == "grammar":
      update = value is not None and value != self.grammar
      # only update the grammar if the grammar is unassigned
      assert(not (update and self.grammar))
    super().__setattr__(name, value)
    if update:
      for child in self.children:
        child.grammar = value
  @assertParse
  def parse(self, succ, **kwargs):
    return partial(succ, **kwargs)
  def str(self):
    return self.sep.join(child.str(self.prec) for child in self.children)
  def str(self, prec):
    return ("?:%s)" if prec < self.prec else "%s") % str(self)
  def __neg__(self):
    return Negative(self)
  def __pos__(self):
    return - - self
  def __or__(lhs, rhs):
    return Choice(children=[lhs,rhs])
  def __and__(lhs, rhs):
    return Sequence(children=[lhs,rhs])
  def __add__(lhs, rhs):
    return +rhs & lhs
  def __sub__(lhs, rhs):
    return -rhs & lhs
  def __rshift__(self, func):
    return YaccMatch(func=func)

from ._choice import Choice
from ._sequence import Sequence
from ._negative import Negative
from ..match import YaccMatch

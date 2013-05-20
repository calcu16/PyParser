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

from ._abstract import AbstractCombinator
from ._abstract import DIE
from ._debug import assertParse, assertSucc, assertFail, assertCont, badcall
from copy import copy
from functools import partial
from queue import PriorityQueue

class Repeat(AbstractCombinator):
  def __init__(self, sym, lower=None, upper=None, greedy=True, *args, **kwargs):
    super().__init__(children=[sym],*args,**kwargs)
    self.lower = lower
    self.upper = upper
    self.greedy = greedy
  def __str__(self):
    greedy = "" if self.greedy else "?"
    if not self.lower and self.upper is None:
      return str(self.children[0]) + "*" + greedy
    elif self.lower == 1 and self.upper is None:
      return str(self.children[0]) + "+" + greedy
    elif self.upper is None:
      return str(self.children[0]) + "{%d,}" % self.lower + greedy
    elif not self.lower and self.upper == 1:
      return str(self.children[0]) + "?" + greedy
    elif self.lower == self.upper:
      return str(self.children[0]) + "{%d}" % self.lower
    elif not self.lower:
      return str(self.children[0]) + "{,%d}" % self.upper + greedy
    else:
      return str(self.children[0]) + "{%d,%d}" % (self.lower,self.upper) + greedy
  @assertParse
  def parse(self, succ, fail, **kwargs):
    value = 0
    count = 0
    greedy = -1 if self.greedy else 1
    queue = PriorityQueue(len(self.children))
    current = (-1, -1, badcall)
    
    @assertCont
    def rcont(fail,**kwargs):
      nonlocal current
      return partial(current[2],fail=rfail)
    
    @assertFail
    def rfail(value, cont, **kwargs):
      global DIE
      nonlocal fail, queue, current, rcont
      last = current[0]
      if value is not None:
        queue.put((last+value,current[1],cont))
      if not queue.qsize():
        return partial(fail,value=None,cont=DIE)
      current = queue.get()
      if current[0] == last:
        return partial(current[2],fail=rfail)
      return partial(fail,value=last-current[0],cont=rcont)
    
    @assertSucc
    def repeat(input, pmatch, fail, **skwargs):
      nonlocal count, greedy, queue, value, succ, rfail
      if self.lower is None or self.lower <= count:
        queue.put((value,greedy*count,partial(succ,input=input.fork(),pmatch=copy(pmatch),fail=rfail,**skwargs)))
      count += 1
      if self.upper is None or count <= self.upper:
        queue.put((value,greedy*count,partial(repeat,input=input,pmatch=pmatch,fail=rfail,**skwargs)))
    
    return partial(repeat,fail=rfail,**kwargs)

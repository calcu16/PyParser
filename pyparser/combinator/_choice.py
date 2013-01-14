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
from ._debug import assertParse, assertSucc, assertCont, assertFail, badcall
from copy import copy
from functools import partial
from queue import PriorityQueue

class Choice(AbstractCombinator):
  def __init__(self, *args, **kwargs):
    super().__init__(prec=2,sep="|",*args, **kwargs)
  
  def makeSucc(self, choice, succ, **kwargs):
    @assertSucc
    def cleanup(pmatch, **skwargs):
      nonlocal self, choice, succ
      for child in self.children[choice+1:]:
        pmatch = child.nomatch(pmatch)
      return partial(succ,pmatch=pmatch,**skwargs)
    @assertSucc
    def setup(pmatch, **skwargs):
      nonlocal self, choice, kwargs
      func = partial(self.children[choice].parse, **kwargs)
      for child in self.children[choice+1:]:
        pmatch = child.nomatch(pmatch)
      return partial(func,pmatch=pmatch,succ=cleanup,**skwargs)
    return setup
  
  @assertParse
  def parse(self, input, fail, pmatch, **kwargs):
    inputs = input.fork(len(self.children))
    queue = PriorityQueue(len(self.children))
    for i, (input,child) in enumerate(zip(inputs,self.children)):
      queue.put((0,i,partial(self.makeSucc(choice=i,**kwargs),input=input,pmatch=copy(pmatch))))
    current = (-1, -1, badcall)
    
    @assertCont
    def ccont(fail, **kwargs):
      nonlocal current
      return partial(current[2],fail=cfail)
    
    @assertFail
    def cfail(value, cont, **kwargs):
      global DIE
      nonlocal fail, queue, current, ccont
      last = current[0]
      if value is not None:
        queue.put((last+value,current[1],cont))
      if not queue.qsize():
        return partial(fail,value=None,cont=DIE)
      current = queue.get()
      if current[0] == last:
        return partial(current[2],fail=cfail)
      return partial(fail,value=last-current[0],cont=ccont)
    return partial(DIE,fail=cfail)

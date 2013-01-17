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
from ._debug import assertParse, assertSucc
from functools import partial

class Match(AbstractCombinator):
  def __init__(self, sym, gen=None, name=None, *args, **kwargs):
    super().__init__(children=[sym], *args, **kwargs)
    self.sym = sym
    self.gen = gen
    self.name = name
  def __str__(self):
    if self.name:
      return "(%s)" % self.sym
    else:
      return "(?P<%s>%s)" % (self.name, self.sym)
  @assertParse
  def parse(self, input, succ, pmatch, **kwargs):
    if self.gen:
      pmatch = self.gen.produce(parent=pmatch, loc=input.loc(), name=self.name)
      assert(pmatch is not None)
    @assertSucc
    def cleanup(pmatch, input, **skwargs):
      nonlocal self, succ
      if pmatch.consume:
        pmatch = pmatch.consume(loc=input.loc(), name=self.name)
      return partial(succ, pmatch=pmatch, input=input, **skwargs)
    return partial(self.sym.parse,input=input,succ=cleanup,pmatch=pmatch,**kwargs)

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

def private():
  from collections import deque
  from weakref import ref
  from copy import copy
  
  global identity
  def identity(val):
    return val
  
  global badcall
  def badcall(*arg, **kwargs):
    assert(False)
  
  global tailEval
  def tailEval(val):
    while callable(val):
      val = val()
    return val
  global begins
  def begins(sub, sup):
    try:
      for s in sub:
        if s != next(sup):
          return False
      return True
    except StopIteration:
      return False
  
  class ForkFactory(object):
    def __init__(self, iterable):
      self.iter     = iter(iterable)
      self.children = []
    def fork(self,seed=deque()):
      child = Fork(self,seed)
      self.children.append(ref(child))
      return child
    def read(self):
      try:
        val = next(self.iter)
      except BaseException as ex:
        def gen(ex):
          while True:
            raise ex
          yield
        val = ex
      else:
        def gen(val):
          while True:
            yield val
      children = []
      for child in self.children:
        child = child()
        if child is not None:
          children.append(ref(child))
          child.deque.append(gen(val))

  class Fork(object):
    def __init__(self, parent, seed = deque()):
      self.parent = parent 
      self.deque  = copy(seed)
      self.index  = 0
    def fork(self, n=1):
      if n == 1:
        return self.parent.fork(self.deque)
      return tuple(self.parent.fork(self.deque) for _ in range(n))
    def __iter__(self):
      return self
    def __next__(self):
      self.index += 1
      if not self.deque:
        self.parent.read()
      return next(self.deque.popleft())
    def __eq__(self, other):
      return type(other) == Fork and \
             self.parent == other.parent and \
             self.index  == other.index
    def __hash__(self):
      return hash(self.parent) ^ hash(self.index)
  
  global fork
  def fork(iterable):
    return ForkFactory(iterable).fork()

  lazy_sentinal = object()
  global lazy
  class lazy(object):
    def __init__(self, func, *args, **kwargs):
      assert(callable(func))
      self.func   = func
      self.args   = args
      self.kwargs = kwargs
    def __call__(self):
      try:
        return self.result
      except AttributeError:
        pass
      self.result = self.func(*self.args, **self.kwargs)
      return self.result
private()

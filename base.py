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
  from itertools import tee
  
  def tailEval(val):
    while callable(val):
      val = val()
    return val
  
  def begins(sub, sup):
    try:
      for s in sub:
        if s != next(sup):
          return False
      return True
    except StopIteration:
      return False
  
  global Match, Lookup
  global any, parse
  
  class ParseObject(object):
    def __init__(self):
      self.prec = 0
    def str(self, prec):
      return ("(% s )" if prec < self.prec else "%s") % str(self)
    def __and__(lhs, rhs):
      return Sequence(lhs, rhs)
    def __or__(lhs, rhs):
      return Choice(lhs, rhs)
    def __neg__(self):
      return Negate(self)
    def __pos__(self):
      return Test(self)
  class Any(ParseObject):
    def __init__(self):
      super(Any,self).__init__()
    def __str__(self):
      return "."
    def parse(self, **kwargs):
      try:
        next(kwargs['input'])
      except StopIteration:
        return kwargs['fail']
      return lambda : kwargs['succ'](input=kwargs['input'])
  class Match(ParseObject):
    def __init__(self, iter):
      super(Match,self).__init__()
      self.iter = list(iter)
    def __str__(self):
      return str(self.iter)
    def parse(self, input, succ, fail, **kwargs):
      return (lambda : succ(input=input)) if begins(self.iter, input) else fail
  class Sequence(ParseObject):
    def __init__(self, *args):
      super(Sequence,self).__init__()
      self.seq = args
      self.prec = 1
    def __str__(self):
      return " & ".join(p.str(self.prec) for p in self.seq)
    def parse(self, input, succ, **kwargs):
      acc = succ
      for p in reversed(self.seq):
        nkwargs = {}
        nkwargs.update(kwargs)
        nkwargs['succ'] = acc
        def bind(p, nkwargs):
          def succ(input, **skwargs):
            nonlocal nkwargs, p
            nkwargs['input'] = input
            return p.parse(**nkwargs)
          return succ
        acc = bind(p, nkwargs)
      return lambda : acc(input=input)
  class Choice(ParseObject):
    def __init__(self, *args):
      super(Choice,self).__init__()
      self.choices = args
      self.prec = 2
    def __str__(self):
      return " | ".join(p.str(self.prec) for p in self.choices)
    def parse(self, input, fail, **kwargs):
      inputs = tee(input, len(self.choices))
      acc = fail
      for i, p in zip(inputs, reversed(self.choices)):
        nkwargs = {}
        nkwargs.update(kwargs)
        nkwargs['input'] = i
        nkwargs['fail']  = acc
        def bind(p, nkwargs):
          def fail2(**fkwargs):
            nonlocal p, nkwargs
            return p.parse(**nkwargs)
          return fail2
        acc = bind(p, nkwargs)
      return acc
  class Negate(ParseObject):
    def __init__(self, other):
      super(Negate,self).__init__()
      self.other = other
    def __str__(self):
      return "-%s" % self.other.str(self.prec)
    def parse(self, input, succ, fail, **kwargs):
      i1, i2 = tee(input)
      kwargs['input'] = i1
      def bind(i2, succ, fail):
        def succ2(**skwargs):
          nonlocal fail
          return fail
        def fail2(**fkwargs):
          nonlocal i2, succ
          fkwargs['input'] = i2
          return succ(**fkwargs)
        return succ2, fail2
      kwargs['succ'], kwargs['fail'] = bind(i2, succ, fail)
      return lambda : self.other.parse(**kwargs)
  class Test(ParseObject):
    def __init__(self, other):
      super(Test,self).__init__()
      self.other = other
    def __str__(self):
      return "+%s" % self.other.str(self.prec)
    def parse(self, input, succ, **kwargs):
      i1, i2 = tee(input)
      kwargs['input'] = i1
      def bind(i2, succ):
        def succ2(**skwargs):
          nonlocal succ, i2
          skwargs['input'] = i2
          return succ(skwargs)
        return succ2
      kwargs['succ']  = bind(i2, succ)
      return lambda : self.other.parse(**kwargs)
  class Lookup(ParseObject):
    def __init__(self, name):
      super(Lookup,self).__init__()
      self.name = name
    def __str__(self):
      return "{%s}" % str(name)
    def parse(self, **kwargs):
      return lambda : kwargs['lookup'][self.name].parse(**kwargs)
  any  = Any()
  def parse(start, lookup, input):
    return tailEval(lookup[start].parse(input=iter(input), lookup=lookup, succ=lambda input : input, fail=lambda : None))
private()

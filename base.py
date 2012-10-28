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
  from util import fork
  from util import identity
  from util import lazy
  from util import tailEval
  from util import begins
  
  def assertParse(func):
    def decorator(*args, **kwargs):
      nonlocal func
      assert(set(kwargs.keys()) == {'input','lookup','succ','fail','matching','inv'})
      return func(*args, **kwargs)
    return decorator
  def assertSucc(func):
    def decorator(*args, **kwargs):
      nonlocal func
      assert(set(kwargs.keys()) == {'match','input','result'})
      return func(*args, **kwargs)
    return decorator
  def assertFail(func):
    def decorator(*args, **kwargs):
      nonlocal func
      assert(set(kwargs.keys()) == set())
      return func(*args, **kwargs)
    return decorator
  
  global parse
  def parse(start, lookup, input):
    parseArgs = {
      'input'     : fork(input),
      'lookup'    : lazy(identity,lookup),
      'succ'      : assertSucc(lambda match, input, **kwargs : (match,input)),
      'fail'      : assertFail(lambda **kwargs : None),
      'matching'  : False,
      'inv'       : None,
    }
    return tailEval(lookup[start].parse(**parseArgs))
  
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
    @assertParse
    def parse(self, input, succ, fail, matching, **kwargs):
      try:
        match = (next(input),)
        if not matching:
          match = ()
      except StopIteration:
        return fail
      return lazy(succ, input=input, match=match, result={})
  global Match
  class Match(ParseObject):
    def __init__(self, match):
      super(Match,self).__init__()
      self.match = tuple(iter(match))
    def __str__(self):
      return str(self.match)
    @assertParse
    def parse(self, input, succ, fail, matching, **kwargs):
      match = self.match if matching else ()
      return lazy(succ,input=input,match=self.match,result={}) if begins(self.match, input) else fail
  class Sequence(ParseObject):
    def __init__(self, *args):
      super(Sequence,self).__init__()
      self.seq = args
      self.prec = 1
    def __str__(self):
      return " & ".join(p.str(self.prec) for p in self.seq)
    @assertParse
    def parse(self, input, succ, **kwargs):
      acc = succ
      for p in reversed(self.seq):
        nkwargs = {}
        nkwargs.update(kwargs)
        def bind(p, acc, nkwargs):
          @assertSucc
          def succ(input, match, **skwargs):
            nonlocal nkwargs, p
            match2 = match
            nkwargs['succ'] = assertSucc(lambda match, **s2kwargs : acc(match=match+match2, **s2kwargs))
            return p.parse(input=input, **nkwargs)
          return succ
        acc = bind(p, acc, nkwargs)
      return lazy(acc,input=input,match=(),result={})
  class Choice(ParseObject):
    def __init__(self, *args):
      super(Choice,self).__init__()
      self.choices = args
      self.prec = 2
    def __str__(self):
      return " | ".join(p.str(self.prec) for p in self.choices)
    @assertParse
    def parse(self, input, fail, **kwargs):
      inputs = input.fork(len(self.choices))
      acc = fail
      for i, p in zip(inputs, reversed(self.choices)):
        nkwargs = {}
        nkwargs.update(kwargs)
        nkwargs['input'] = i
        nkwargs['fail']  = acc
        def bind(p, nkwargs):
          return assertFail(lambda **fkwargs : p.parse(**nkwargs))
        acc = bind(p, nkwargs)
      return acc
  class Negate(ParseObject):
    def __init__(self, other):
      super(Negate,self).__init__()
      self.other = other
    def __str__(self):
      return "-%s" % self.other.str(self.prec)
    @assertParse
    def parse(self, input, succ, fail, **kwargs):
      finput = input.fork()
      def bind(input, succ, fail):
        return assertSucc(lambda **skwargs : fail), \
               assertFail(lambda **fkwargs : succ(input=input, **fkwargs))
      succ, fail = bind(finput, succ, fail)
      return lambda : self.other.parse(input=input,succ=succ,fail=fail,**kwargs)
  class Test(ParseObject):
    def __init__(self, other):
      super(Test,self).__init__()
      self.other = other
    def __str__(self):
      return "+%s" % self.other.str(self.prec)
    @assertParse
    def parse(self, input, succ, **kwargs):
      sinput = input.fork()
      def bind(input, succ):
        return assertSucc(lambda **skwargs : succ(input=input, **skwargs))
      succ = bind(sinput, succ)
      return lambda : self.other.parse(input=input,succ=succ,**kwargs)
  global Lookup
  class Lookup(ParseObject):
    def __init__(self, name):
      super(Lookup,self).__init__()
      self.name = name
    def __str__(self):
      return "{%s}" % str(name)
    @assertParse
    def parse(self, lookup, **kwargs):
      return lambda : lookup()[self.name].parse(lookup=lookup, **kwargs)
  global any
  any  = Any()
  
private()

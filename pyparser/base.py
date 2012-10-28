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
  from .util import begins, fork, identity, lazy, tailEval
  
  # make sure all parse arguments are correct
  def assertParse(func):
    def decorator(*args, **kwargs):
      nonlocal func
      assert(set(kwargs.keys()) == {'input','lookup','succ','fail','matching','inv'})
      return func(*args, **kwargs)
    return decorator
  # make sure all succ arguments are correct
  def assertSucc(func):
    def decorator(*args, **kwargs):
      nonlocal func
      assert(set(kwargs.keys()) == {'match','input','result'})
      return func(*args, **kwargs)
    return decorator
  # make sure all fail arguments are correct
  def assertFail(func):
    def decorator(*args, **kwargs):
      nonlocal func
      assert(set(kwargs.keys()) == set())
      return func(*args, **kwargs)
    return decorator
  
  # parse a string given a start and lookup table
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
  
  # superclass for all parse objects
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
  # reads in any value
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
  # matches exactly a single value
  global Pattern
  class Pattern(ParseObject):
    def __init__(self, pattern):
      super(Pattern,self).__init__()
      self.pattern = tuple(iter(pattern))
    def __str__(self):
      return str(self.match)
    @assertParse
    def parse(self, input, succ, fail, matching, **kwargs):
      match = self.pattern if matching else ()
      return lazy(succ,input=input,match=match,result={}) if begins(self.pattern, input) else fail
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
        def bind(p, input, fail, kwargs):
          return assertFail(lambda **fkwargs : p.parse(input=input,fail=fail,**kwargs))
        acc = bind(p, i, acc, kwargs)
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
               assertFail(lambda input, **fkwargs : succ(input=input, **fkwargs))
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
      def bind(sinput, succ):
        return assertSucc(lambda input, **skwargs : succ(input=sinput, **skwargs))
      succ = bind(sinput, succ)
      return lazy(self.other.parse,input=input,succ=succ,**kwargs)
  global Lookup
  class Lookup(ParseObject):
    def __init__(self, name):
      super(Lookup,self).__init__()
      self.name = name
    def __str__(self):
      return "{%s}" % str(self.name)
    @assertParse
    def parse(self, lookup, **kwargs):
      return lazy(lookup()[self.name].parse, lookup=lookup, **kwargs)
  class Match(ParseObject):
    def __init__(self, match, name):
      super(Match,self).__init__()
      self.name = name
      self.match = match
    def __str__(self):
      return "<%s=%s>" % (str(name), str(self.match))
  class Capture(ParseObject):
    def __init__(self, match, name, func=identity):
      super(Capture,self)._init__()
      self.match = match
      self.func  = func
      self.name  = name
    def __str__(self):
      return "<%s:%s(%s)>" % (str(self.name), str(self.func.__name__), str(self.match))
    @assertParse
    def parse(self, lookup, **kwargs):
      return 
  global any
  any  = Any()
  
  
private()

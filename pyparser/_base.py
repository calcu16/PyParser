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
  from copy import copy
  from functools import partial
  from queue import PriorityQueue
  from sys import stderr
  from ._util import begins, fork, identity, tailEval, badcall
  DEBUGGING = None
  def DEBUG(self, input, **kwargs):
    nonlocal DEBUGGING
    if DEBUGGING:
      input = list(input.fork())
      print("DEBUG : %s >> %s" % (input, self), file=DEBUGGING)
  def ASSERTEQ(
  a, b):
    if DEBUGGING and not a == b:
      print("%s != %s" % (a, b), file=DEBUGGING)
    assert(a == b)
  # make sure all parse arguments are correct
  def assertParse(func):
    def decorator(*args, **kwargs):
      nonlocal func
      ASSERTEQ(set(kwargs.keys()), {'input','succ','fail','matching','inv','isstr'})
      DEBUG(*args, **kwargs)
      return func(*args, **kwargs)
    return decorator
  # make sure all succ arguments are correct
  def assertSucc(func):
    def decorator(*args, **kwargs):
      nonlocal func
      ASSERTEQ(set(kwargs.keys()), {'match','input','result','fail'})
      return func(*args, **kwargs)
    return decorator
  # make sure all fail arguments are correct
  def assertFail(func):
    def decorator(*args, **kwargs):
      nonlocal func
      ASSERTEQ(set(kwargs.keys()), {'value','cont'})
      assert(kwargs['value'] != 0)
      return func(*args, **kwargs)
    return decorator
  # make sure all continuation arguments are correct
  def assertCont(func):
    def decorator(*args, **kwargs):
      nonlocal func
      ASSERTEQ(set(kwargs.keys()), {'fail'})
      return func(*args, **kwargs)
    return decorator
  
  global Grammar
  class Grammar(object):
    def __init__(self):
      self.lookup   = {}
    def __setitem__(self, name, item):
      self.lookup[name] = item
      item.grammar = self
    def __getitem__(self, name):
      return Lookup(name=name,grammar=self)
  
  @assertSucc
  def SUCC(match, input, result, **kwargs):
    return result, input
  @assertFail
  def FAIL(value, cont, **kwargs):
    if value is None:
      return None
    else:
      return partial(cont,fail=FAIL)
  class ParseObject(object):
    def __init__(self, grammar=None, children=(), *args, **kwargs):
      super(ParseObject,self).__setattr__('grammar',None)
      self.children = tuple(children)
      self.grammar  = grammar
      self.prec     = 0
    def __setattr__(self, name, value):
      update = False
      if name == "grammar":
        assert(value is None or issubclass(type(value), Grammar))
        update = value is not None and value != self.grammar
        # only update the grammar if the grammar is unassigned
        if update:
          assert(self.grammar is None)
      super(ParseObject,self).__setattr__(name, value)
      if update:
        for child in self.children: child.grammar = value
    def str(self, prec):
      return ("( %s )" if prec < self.prec else "%s") % str(self)
    def __or__(lhs, rhs):
      return Choice(children=[lhs,rhs])
    def __and__(lhs, rhs):
      return Sequence(children=[lhs,rhs])
    def __call__(self, name):
      return Save(self, name)
    def __lshift__(self, input):
      nonlocal SUCC, FAIL
      assert(self.grammar is not None)
      parseArgs = {
        'input'     : fork(input),
        'succ'      : SUCC,
        'fail'      : FAIL,
        'matching'  : False,
        'inv'       : None,
        'isstr'     : type(input) == str
      }
      return tailEval(self.parse(**parseArgs))
  DIE = lambda fail : partial(fail,value=None,cont=badcall)
  NOMATCH = lambda isstr : "" if isstr else ()
  # matches any value
  global Any
  class Any(ParseObject):
    def __init__(self, count = 1, *args, **kwargs):
      super(Any,self).__init__(*args,**kwargs)
      self.count = count
    def __str__(self):
      if self.count <= 0: return ""
      if self.count == 1: return "."
      return ".{%d}" % self.count
    @assertParse
    def parse(self, input, succ, fail, matching, isstr, **kwargs):
      match = tuple(next(input) for i in range(self.count))
      if len(match) < self.count:
        nonlocal DIE
        return DIE(fail)
      if not matching:
        match = ()
      if isstr:
        match = "".join(match)
      return partial(succ, input=input, match=match, result={}, fail=fail)
  def defaultMatch(match, result):
    return match if not result else result
  # matches the value and saves it in the dictionary
  class Save(ParseObject):
    def __init__(self, sym, name, func=defaultMatch, *args, **kwargs):
      super(Save,self).__init__(grammar=sym.grammar, children=[sym], *args, **kwargs)
      self.sym  = sym
      self.name = name
      self.func = func
    def __str__(self):
      return "(?P<%s>%s)" % (self.name, self.sym)
    @assertParse
    def parse(self, succ, matching, isstr,**kwargs):
      def save(match, result, **skwargs):
        nonlocal self, succ, matching
        result = {self.name : self.func(match=match,result=result)}
        if not matching:
          match = ()
        if isstr:
          match = "".join(match)
        return partial(succ,match=match,result=result,**skwargs)
      return partial(self.sym.parse,succ=save,matching=True,isstr=isstr,**kwargs)
  # fails to parse
  global Fail
  class Fail(ParseObject):
    def __init__(self, value=None, *args, **kwargs):
      super(Fail,self).__init__(*args, **kwargs)
      self.value = value
    def __str__(self):
      return "!" if self.value is None else "#%d" % self.value
    @assertParse
    def parse(self, fail, succ, input, isstr, **kwargs):
      @assertCont
      def cont(fail, **ckwargs):
        nonlocal succ, input, isstr
        return partial(succ,input=input,match=NOMATCH(isstr),result={},fail=fail)
      return partial(fail,value=self.value,cont=cont)
  global Pattern
  class Pattern(ParseObject):
    def __init__(self, pattern=(), *args, **kwargs):
      super(Pattern,self).__init__(*args,**kwargs)
      self.pattern = tuple(iter(pattern))
    def __str__(self):
      return str(self.pattern)
    @assertParse
    def parse(self, input, succ, fail, matching, isstr, **kwargs):
      match = self.pattern if matching else ()
      if isstr:
        match = "".join(match)
      if begins(self.pattern, input):
        return partial(succ,input=input,match=match,result={},fail=fail)
      else:
        nonlocal DIE
        return DIE(fail)
  # a sequence of symbols
  class Sequence(ParseObject):
    def __init__(self, *args, **kwargs):
      super(Sequence,self).__init__(*args,**kwargs)
      self.prec = 1
    def __str__(self):
      return "".join(p.str(self.prec) for p in self.children)
    @assertParse
    def parse(self, input, succ, fail, isstr, **kwargs):
      acc = succ
      for p in reversed(self.children):
        nkwargs = {}
        nkwargs.update(kwargs)
        def bind(p, acc, nkwargs):
          @assertSucc
          def succ(input, match, result, **skwargs):
            nonlocal nkwargs, p, fail, isstr
            match2 = match
            result2 = copy(result)
            def succ2(match, result, **s2kwargs):
              nonlocal match2, result2
              result2.update(result)
              match2 = match + match2
              return partial(acc,match=match2, result=result2, **s2kwargs)
            nkwargs['succ'] = succ2
            return partial(p.parse,input=input,fail=fail,isstr=isstr,**nkwargs)
          return succ
        acc = bind(p, acc, nkwargs)
      return partial(acc,input=input,match=NOMATCH(isstr),result={},fail=fail)
  # an ordered choice
  class Choice(ParseObject):
    def __init__(self, *args, **kwargs):
      super(Choice,self).__init__(*args,**kwargs)
      self.prec = 2
    def __str__(self):
      return "|".join(p.str(self.prec) for p in self.choices)
    @assertParse
    def parse(self, input, fail, **kwargs):
      inputs = input.fork(len(self.children))
      queue  = PriorityQueue(len(self.children))
      for i, (input,child) in enumerate(zip(inputs,self.children)):
        queue.put((0, i, partial(child.parse,input=input,**kwargs)))
      current= queue.get()
      @assertCont
      def cont2(fail, **kwargs):
        nonlocal queue, current, DIE
        assert(current != None)
        return current[2](fail=fail2)
      @assertFail
      def fail2(value,cont,**kwargs):
        nonlocal fail, queue, current, DIE
        last = current[0]
        if value is not None:
          queue.put((last + value, current[1], cont))
        if not queue.qsize():
          return partial(fail,value=None,cont=DIE)
        current = queue.get()
        if current[0] == last:
          return partial(current[2],fail=fail2)
        return partial(fail,value=last-current[0],cont=cont2)
      return current[2](fail=fail2)
  # a lookup
  class Lookup(ParseObject):
    def __init__(self, name, *args, **kwargs):
      super(Lookup,self).__init__(*args, **kwargs)
      self.name = name
    def __str__(self):
      return("(?$%s)" % name)
    @assertParse
    def parse(self, **kwargs):
      return partial(self.grammar.lookup[self.name].parse, **kwargs)
private()

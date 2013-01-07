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
  from ._match import ParseMatch
  DEBUGGING = None
  def DEBUG(self, input, **kwargs):
    nonlocal DEBUGGING
    if DEBUGGING:
      input = list(input.fork())
      print("DEBUG : %s >> %s" % (input, self), file=DEBUGGING)
  def ASSERTEQ(a, b):
    if DEBUGGING and not a == b:
      print("%s != %s" % (a, b), file=DEBUGGING)
    assert(a == b)
  # make sure all parse arguments are correct
  def assertParse(func):
    def decorator(*args, **kwargs):
      nonlocal func
      ASSERTEQ(set(kwargs.keys()), {'input','succ','fail','pmatch','inv'})
      DEBUG(*args, **kwargs)
      return func(*args, **kwargs)
    return decorator
  # make sure all succ arguments are correct
  def assertSucc(func):
    def decorator(*args, **kwargs):
      nonlocal func
      ASSERTEQ(set(kwargs.keys()), {'pmatch','input','fail'})
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
  def SUCC(pmatch, input, **kwargs):
    return pmatch, input
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
      for child in children:
        self.grammar = child.grammar
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
      return ("(?:%s)" if prec < self.prec else "%s") % str(self)
    def __or__(lhs, rhs):
      return Choice(children=[lhs,rhs])
    def __and__(lhs, rhs):
      return Sequence(children=[lhs,rhs])
    def __call__(self, name=None):
      return Save(self, name)
    def __lshift__(self, input):
      nonlocal SUCC, FAIL
      assert(self.grammar is not None)
      parseArgs = {
        'input'     : fork(input),
        'succ'      : SUCC,
        'fail'      : FAIL,
        'pmatch'    : ParseMatch(start=0, isstr=issubclass(type(input),str)),
        'inv'       : None,
      }
      return tailEval(self.parse(**parseArgs))
    def nomatch(self, pmatch, seen = set()):
      if self in seen: return
      seen = copy(seen)
      seen.add(self)
      for child in self.children:
        child.nomatch(seen)
  DIE = lambda fail : partial(fail,value=None,cont=badcall)
  # a grammar lookup
  class Lookup(ParseObject):
    def __init__(self, name, *args, **kwargs):
      super(Lookup,self).__init__(*args, **kwargs)
      self.name = name
    def __str__(self):
      return("(?$%s)" % name)
    @assertParse
    def parse(self, **kwargs):
      return partial(self.grammar.lookup[self.name].parse, **kwargs)
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
    def parse(self, input, succ, fail, pmatch, **kwargs):
      match = tuple(next(input) for i in range(self.count))
      if len(match) < self.count:
        nonlocal DIE
        return DIE(fail)
      pmatch += match
      return partial(succ, input=input, pmatch=pmatch, fail=fail)
  global Pattern
  class Pattern(ParseObject):
    def __init__(self, pattern=(), *args, **kwargs):
      super(Pattern,self).__init__(*args, **kwargs)
      self.pattern = pattern
    def __str__(self):
      return str(self.pattern)
    @assertParse
    def parse(self, input, succ, fail, pmatch, **kwargs):
      nonlocal DIE
      if begins(self.pattern, input):
        pmatch += self.pattern
        return partial(succ,input=input,pmatch=pmatch,fail=fail)
      return DIE(fail)
  # matches a value and saves it in the match object
  class Save(ParseObject):
    def __init__(self, sym, name=None, *args, **kwargs):
      super(Save,self).__init__(children=[sym], *args, **kwargs)
      self.sym  = sym
      self.name = name
    def __str__(self):
      if name:
        return "(%s)" % self.sym
      else:
        return "(?P<%s>%s)" % (self.name, self.sym)
    @assertParse
    def parse(self, input, succ, pmatch, **kwargs):
      opmatch = pmatch
      pmatch  = opmatch.child(start=input.loc(), name=self.name)
      #assertSucc
      def cleanup(pmatch, **skwargs):
        nonlocal self, opmatch, succ
        opmatch += pmatch
        return partial(succ,pmatch=opmatch,**skwargs)
      return partial(self.sym.parse,input=input,succ=cleanup,pmatch=pmatch,**kwargs)
    def nomatch(self, pmatch, seen=set()):
      if self not in seen:
        pmatch.nochild(self.name)
      super(Save,self).nomatch(pmatch=pmatch,seen=seen)
  # fails to parse
  global Fail
  class Fail(ParseObject):
    def __init__(self, value=None, *args, **kwargs):
     super(Fail,self).__init__(*args,**kwargs)
     self.value = value
private()

#!/usr/bin/env python
# Copyright (c) 2013, Andrew Carter
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
  from .. import BasicMatch
  def lift(match, default=None):
    return match._result if match else default
  global Match
  class Match(object):
    def __init__(self, start=0, result=None, parent=None, matching=False):
      self._start     = start
      self._end       = None
      self._groups    = []
      self._groupdict = {}
      self._parent    = parent
      self._matching  = matching
      self._loc       = 0
      if result is None:
        self._result    = ""
      else:
        self._result    = result
    def parent(self, **kwargs):
      return self._parent
    def root(self):
      return self if self._parent is None else self._parent
    def _add(self, value, name=None):
      if self._parent is not None:
        self._parent._add(value, name)
      if name is None:
        if value is not None and self._loc < len(self._groups):
          self._groups[self._loc] = value
        elif self._loc == len(self._groups):
          self._groups.append(value)
        self._loc += 1
      elif value is not None or name not in self._groupdict:
        self._groupdict[name] = value
    def child(self, loc, name=None, **kwargs):
      pmatch = Match(start=loc, parent=self, matching=True)
      self._add(pmatch)
      if name is not None:
        self._add(pmatch, name)
      return pmatch
    def nochild(self, name=None):
      self._add(None)
      if name is not None:
        self._add(None, name)
      if self._parent:
        self._parent.nochild(name)
    def __iadd__(self, rhs):
      if self._parent is not None:
        self._parent += rhs
      if not self._matching:
        pass
      elif issubclass(type(rhs), Match):
        self._result += rhs._result
      else:
        self._result += "".join(rhs)
      return self
    def group(self, arg, *args):
      if not args:
        if arg == 0:
          return self.result
        try:
          return self._groups[arg-1].result
        except TypeError:
          return self._groupdict[arg].result
      return tuple(self.group(arg) for arg in (arg,) + args)
    def groups(self, default=None):
      return tuple(lift(group, default)
                      for group in self._groups)
    def groupdict(self, default=None):
      return dict((key, lift(value, default))
                      for key, value in self._groupdict.items())

private()
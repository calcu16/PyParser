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

from .._util import identity
from copy import copy

_sentinel = object()
class AbstractMatch(object):
  def __init__(self, parent=None, copy=None, consume=_sentinel, iadd=_sentinel, result=_sentinel, capture=_sentinel, name=_sentinel, *args, **kwargs):
    self.parent = parent
    if copy is not None:
      self.result   = copy.result if result is _sentinel else result
      self._consume = copy._consume if consume is _sentinel else consume
      self._iadd    = copy._iadd if iadd is _sentinel else iadd
      self.capture  = copy.capture if capture is _sentinel else capture
      self.name     = copy.name if name is _sentinel else name
    else:
      self.result   = None if result is _sentinel else result
      self._consume = identity if consume is _sentinel else consume
      self._iadd    = None if iadd is _sentinel else iadd
      self.capture  = True if capture is _sentinel else capture
      self.name     = None if name is _sentinel else name
  def __iadd__(self, rhs):
    if self._iadd:
      self.result = self._iadd(lhs=self.result, rhs=rhs, name=name)
    return self
  def nochild(self, *args, **kwargs):
    return self
  def produce(self, parent=None, **kwargs):
    return type(self)(parent=parent,copy=self,**kwargs)
  def consume(self, **kwargs):
    if self.parent and self._consume:
      self.parent += self._consume(self.result)
    return self.parent

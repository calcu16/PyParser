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

from .._util import fork
DEBUGGING = None

def DEBUG(self, input, **kwargs):
  global DEBUGGING
  if DEBUGGING:
    input = list(input.fork())
    print("DEBUG : %s >> %s" % (input, self), file=DEBUGGING)
def ASSERTEQ(a, b):
  global DEBUGGING
  if DEBUGGING and not a == b:
    print("%s != %s" % (a, b), file=DEBUGGING)
  assert(a == b)
# make sure all parse arguments are correct
def assertParse(func):
  def decorator(*args, **kwargs):
    nonlocal func
    ASSERTEQ(set(kwargs.keys()), {'input','succ','fail','pmatch'})
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

def badcall(*arg, **kwargs):
  assert(False)

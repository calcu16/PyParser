def private():
  def lift(match, default=None):
    return match._result if match else default
  global ParseMatch
  class ParseMatch(object):
    def __init__(self, start=None, result=None, parent=None, isstr=False, matching=False):
      self._start     = start
      self._end       = None
      self._groups    = []
      self._groupdict = {}
      self._parent    = parent
      self._isstr     = isstr
      self._matching  = matching
      self._loc       = 0
      if result is None:
        self._result    = "" if isstr else ()
      else:
        self._result    = result
    def loc(self,value=None):
      old = self._loc
      if value is not None:
        if self._parent:
          self._parent.loc(self._parent.loc() + self._loc - value)
        self._loc = value
      return old
    def parent(self):
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
    def child(self, start, name=None):
      pmatch = ParseMatch(start=start, parent=self, isstr=self._isstr, matching=True)
      self._add(pmatch)
      if name is not None:
        self._add(pmatch, name)
      return pmatch
    def nochild(self, name=None):
      self._add(None)
      if name is not None:
        self._add(None, name)
    def __iadd__(self, rhs):
      if self._parent is not None:
        self._parent += rhs
      if not self._matching:
        pass
      elif issubclass(type(rhs), ParseMatch):
        self._result += rhs._result
      elif self._isstr:
        self._result += "".join(rhs)
      else:
        self._result += tuple(iter(rhs))
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
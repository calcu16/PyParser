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
      self.loc        = 0
      if result is None:
        self._result    = "" if isstr else ()
      else:
        self._result    = result
    def _add(self, value, name=None):
      if name is None:
        if value is not None and self.loc < len(self._groups):
          self._groups[self.loc] = value
        elif self.loc == len(self._groups):
          self._groups.append(value)
        self.loc += 1
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
      if issubclass(type(rhs), ParseMatch):
        if self._matching:
          self._result += rhs._result
        for group in rhs._groups:
          self._add(group)
        for key,value in rhs._groupdict.items():
          self._add(value, key)
      elif not self._matching:
        pass
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
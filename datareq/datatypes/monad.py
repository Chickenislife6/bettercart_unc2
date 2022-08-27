from abc import abstractmethod


class Option:
  @abstractmethod
  def __init__(self, value):
    self.value = value

  @abstractmethod
  def bind(self, f):
    None
    
  @abstractmethod  
  def unwrap(self, f):
    None


class Ok(Option):
  def __init__(self, value):
    self.value = value
  
  def bind(self, f):
    return f(self.value)
  
  def unwrap(self):
    return self.value


class Err(Option):
  def __init__(self, value):
    self.value = value

  def bind(self, f):
    return Err(self.value)

  def unwrap(self):
    raise self.value
    print(self.value)
    quit()
    return self.value

def match(a: Option, f1, f2):
  if isinstance(a, Ok):
    return f1(a.unwrap())
  if isinstance(a, Err):
    return f2(a.unwrap())
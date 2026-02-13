class ArithmeticProgression():
  def __init__(self, begin, step, end):
    self.begin = begin 
    self.step = step 
    self.end = end 
    
  def __iter__(self):
    yield self.begin
    
    for i in range(self.end - 1):
      self.begin += self.step
      yield self.begin

ap = ArithmeticProgression(0,1,3)
print(list(ap))
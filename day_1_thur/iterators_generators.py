# TODO: write a function that takes in a sentence, then makes it an iterable of words, while also adding the __rep__, and __len__ methods

# TODO: creat an iterator from a string and using a while loop, print the values until it raises stop iterator error 

# TODO: write the iterator class, showing how it inherist and checks against other classes

from abc import abstractmethod
import collections.abc as ABC

print(isinstance('jay stance', ABC.Iterable))



class MyNumber():      # here MyNumber class is an iterable
  def __init__(self, number):
    self.number = number
    
  def __repr__(self):
    return f"number is {self.number}"
  
  def __iter__(self):
    return MyNumberIterator(self.number)

class MyNumberIterator(ABC.Iterable):
  
  # __slots__ = ()
  def __init__(self, count):
    self.count = count
  
  # @abstractmethod
  def __next__ (self):
    self.count += 1
    
    if(self.count > 3):
      raise StopIteration
    else:
      return self.count
  
  def __iter__(self):     # in python classes, every method must have self as the first argument
    return self        # iterators must return themselves
  
  
my_num = iter(MyNumber(0))
print(next(my_num))
print(next(my_num))
print(next(my_num))
print(next(my_num))
# my_iterator = MyNumberIterator(0)
# print(my_iterator)
# print(next(my_iterator))
# print(next(my_iterator))
# print(next(my_iterator))
# print(next(my_iterator))


# ===============================

 #          GENERATORS 

#  ===============================

def gen_123():
  print("start")
  yield 1
  print("contiue")
  yield 2
  print("end")
  yield 3
  
for i in gen_123():
  print("-->", i)   # this one prints after the gen function has yielded a value, meaning the print in gen would log first
  
g = gen_123()
print(next(g))
print(next(g))
print(next(g))
print(next(g))


import re
import reprlib
RE_WORD = re.compile('\w+')

class Sentence:
  def __init__(self, text):
    self.text = text

  def __repr__(self):
    return 'Sentence(%s)' % reprlib.repr(self.text)
  
  def __iter__(self):
    for match in RE_WORD.finditer(self.text):
      yield match.group()
      


def gen_123():
  print("start")
  yield 1
  print("contiue")
  yield 2
  print("end")
  yield 3

list_comprehension = [x*3 for x in gen_123()]     # this one precomputes all the ansers and stores it in the array

for i in list_comprehension:
  print(i)

gen_expression = (x*3 for x in gen_123())   # this generates a generator expression that gets the values on demand

for i in gen_expression:
  print(i)


class ArithmeticProgression():
  def __init__(self, begin, step, end = None):
    self.begin = begin 
    self.step = step 
    self.end = end 
    
  def __iter__(self):
    # get result to be in the right type
    result = type(self.begin + self.step)(self.begin)
    index = 0
    forever = self.end is None
    
    while forever or result < self.end:
      yield result 
      index += 1
      # result += self.step
      result = self.begin + (self.step * index)   # this is to reduce the cumulative effect of errors when working with floats

ap = ArithmeticProgression(0,1,3)
print(list(ap))
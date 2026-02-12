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
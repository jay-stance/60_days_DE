import itertools

def isVowel(c):
  return c.lower() in "aeiou"

filterRes = filter(isVowel, 'jaystance')
print(filterRes)
print(list(filterRes))
print(next(filterRes))
print(next(filterRes))
print(next(filterRes))
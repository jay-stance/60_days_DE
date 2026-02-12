def gen_123():
  print("start")
  yield 1
  print("contiue")
  yield 2
  print("end")
  yield 3

list_comprehension = [x*3 for x in gen_123()]

for i in list_comprehension:
  print(i)

gen_expression = (x*3 for x in gen_123())

for i in gen_expression:
  print(i)

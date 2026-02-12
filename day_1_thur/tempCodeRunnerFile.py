def gen_123():
  print("start")
  yield 1
  print("contiue")
  yield 2
  print("end")
  yield 3
  
for i in gen_123():
  print("-->", i)

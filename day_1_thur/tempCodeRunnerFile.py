import itertools

# An iterator that yields numbers (could be a massive file stream)
data_stream = (x for x in range(5))

# Split it into two independent streams
stream_A, stream_B = itertools.tee(data_stream, 2)

print(list(stream_A)) 
# Output: [0, 1, 2, 3, 4]

print(list(stream_B)) 
# Output: [0, 1, 2, 3, 4] (It works a second time!)
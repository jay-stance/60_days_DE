import itertools

merged_chain = itertools.chain('ABC', range(2))

print(merged_chain)
print(list(merged_chain))

# merge_zip = zip(range(4), "abcdef")
merge_zip = itertools.zip_longest(range(4), "abcdef", fillvalue="Nothing here")
print(merge_zip)
print(list(merge_zip))

merge_product = itertools.product('abc', repeat=2)
print(list(merge_product))
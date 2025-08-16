a = ['a', 'b', 'c']
b = [1, 2, 3]
c = list(zip(a, b))

print(c)
print([a for a, b in c if a != 'b'])
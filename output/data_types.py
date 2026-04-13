# Lists are mutable, meaning they can be changed after creation
list_example = [1, 2, 3]
list_example[0] = 10
print(list_example)

tuple_example = (1, 2, 3)
# Tuples are immutable, trying to change them will result in an error
# tuple_example[0] = 10
print(tuple_example)
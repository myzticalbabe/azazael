def calculate(items):
    total = 0
    for item in items:
        total = total + item
    return total


result = calculate([1, 2, 3, 4, 5])
print(result)

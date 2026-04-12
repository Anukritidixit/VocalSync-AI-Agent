class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return ComplexNumber(self.real + other.real, self.imag + other.imag)

    def __str__(self):
        return f'{self.real} + {self.imag}i'

# Create complex numbers
num1 = ComplexNumber(3, 2)
num2 = ComplexNumber(1, 7)

# Calculate sum
sum_num = num1 + num2

print(f'Sum: {sum_num}')
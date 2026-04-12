class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag
    def multiply(self, other):
        return Complex(self.real*other.real - self.imag*other.imag, self.real*other.imag + self.imag*other.real)
    def __str__(self):
        return f'{self.real} + {self.imag}i'

# Example usage:
c1 = Complex(1, 2)
c2 = Complex(3, 4)
result = c1.multiply(c2)
print(f'Multiplication of {c1} and {c2} is: {result}'
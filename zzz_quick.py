from dataclasses import dataclass


@dataclass
class Book:
    title: str
    author: str
    pages: int
    in_stock: bool = True


b1 = Book("1984", "George Orwell", 328)
b2 = Book("1984", "George Orwell", 328)

print(b1)
print(b1 == b2)

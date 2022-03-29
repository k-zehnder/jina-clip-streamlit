from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class Builder(ABC):
    """
    The Builder interace specifies methods for creating the different parts of the Product objects.
    """

    @property
    @abstractmethod
    def product(self) -> None:
        pass

    @abstractmethod
    def produce_part_a(self) -> None:
        pass

    @abstractmethod
    def produce_part_b(self) -> None:
        pass

class ConcreteBuilder1(Builder):
    pass

class Product1:
    def __init__(self) -> None:
        self.parts = []

    def add(self, step) -> None:
        self.parts.append(step)

    def list_parts(self) -> None:
        print(f'Product parts: {", ".join(self.parts)}', end='')

class Director:
    pass
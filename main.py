from objs.builder import Director, ConcreteBuilder1


if __name__ == '__main__':
    director = Director()
    builder = ConcreteBuilder1()
    director.builder = builder

    print('Standard basic product: ')
    director.build_minimal_viable_product()
    builder.product.list_parts()
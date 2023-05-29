import auxiliary
binary_search = auxiliary.binary_search_value

def binary_search_tests():
    try: binary_search([1,2,3,4,5], 0, strict = False)
    except Exception as e: yield True
    else: yield False

    try: binary_search([1,2,3,4,5], 0, strict = True)
    except ValueError as e: yield True
    else: yield False

    yield binary_search([1,2,3,4,5], 1, strict = False) == 1
    yield binary_search([1,2,3,4,5], 1, strict = True) == 1
    yield binary_search([1,2,3,4,5], 2, strict = False) == 2
    yield binary_search([1,2,3,4,5], 3, strict = True) == 3
    yield binary_search([1,2,3,4,5], 4, strict = False) == 4
    yield binary_search([1,2,3,4,5], 5, strict = True) == 5
    yield binary_search([1,2,3,4,5], 6, strict = False) == 5
    try: binary_search([1,2,3,4,5], 6, strict = True)
    except ValueError as e: yield True

    yield binary_search([-1,2,-3,4,5], 4, key = lambda n:n**2, strict = False) == 2
    yield binary_search([['Bob', 2],['Ava', 4],['Tim', 6],['Sam', 7]], 6, lambda item:item[1], strict = False) == ['Tim', 6]

    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    print((binary_search([Person('Bob', 2),Person('Ava', 4),Person('Tim', 6),Person('Sam', 7)], 7, lambda item:item.age, strict = False)).__dict__)
    yield



if __name__ == '__main__':

    binary_search_results = binary_search_tests()

    while True:
        try:
            if next(binary_search_results):
                print(True)
            else: breakpoint()

        except ValueError as e:
            print(e)

        except StopIteration:
            break


import math
from Crypto.Cipher import AES
from Crypto.Random import random, get_random_bytes

def encrypt_with_random_AES(plaintext):
    aes = get_random_bytes(16)
    aes_cipher = AES.new(aes, AES.MODE_EAX)
    nonce = aes_cipher.nonce
    ciphertext, tag = aes_cipher.encrypt_and_digest(plaintext)
    return [aes, ciphertext, nonce, tag]

def binary_search(array, item, strict = False):
    middle = math.floor(len(array)/2)

    if len(array) == 0:
        if strict == False: return -1
        else: raise ValueError


    elif array[middle] == item:
        return middle

    elif array[middle] > item:
        return binary_search(array[:middle], item)

    elif array[middle] < item:
        return middle+1 + binary_search(array[middle+1:], item)


def linear_search(array, item):
    for i, val in enumerate(array):
        if val == item: return i
    else: raise ValueError


def mixed_search(array, item, prefix_len):
    try:
        binary_search(array[:prefix_len], item, strict = True)
    except:
        linear_search(array[prefix_len:], item)


def bubble_sort(array, max_passes = None):

    # Algorithm will usually return a sorted array unless it requires more than max_passes.
    # Then it will just perform max_passes of bubble sort and return

    # PROBLEM: bubble_sort is O(n) AMORTISED for each insert
    # That's not good enough - may as well just do linear search every time.
    # Unless we assume that searches are more common than inserts
    # Which is probably the case sometimes
    # That being said, it means we don't need mixed search and can just do binary

    if max_passes is None: max_passes = len(array)

    for i in range(min(len(array), max_passes)):
        swapped = False
        for j in range(len(array)-1, 0, -1):
            if array[j] < array[j-1]:
                array[j], array[j-1] = (array[j-1], array[j])
                swapped = True
        if not swapped: return array
    return array



if __name__ == '__main__':
    array = [1,3,6,10,15,21,28,36,45,55,21,86,2,4,6,7,22,4,2,-1]
    array = bubble_sort(array)
    print(array)

    search_tests = [4,21,-1,86,39,87,-2]

    for item in search_tests:
        ind = binary_search(array, item)
        if ind == -1: print('TOO SMALL')
        else:print(array[ind])




import math
from Crypto.Cipher import AES
from Crypto.Random import random, get_random_bytes

def get_new_random_ID(banned_list):
    max = 1000
    ID = random.randint(1, max)
    while ID in banned_list:
        max *= 2
        ID = random.randint(1, max)
    return ID
def encrypt_with_random_AES(plaintext):
    aes = get_random_bytes(16)
    aes_cipher = AES.new(aes, AES.MODE_EAX)
    nonce = aes_cipher.nonce
    ciphertext, tag = aes_cipher.encrypt_and_digest(plaintext)
    return [aes, ciphertext, nonce, tag]

def generate_password():
    consonant_letters = ["a", "b", "c", "d", "e", "f", "g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    consonant_pairs = ['bl', 'br', 'ch', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'kl', 'kr', 'ph', 'pl', 'pr',
                       'sc', 'sh', 'sk', 'sl', 'sm', 'sn', 'sp', 'st', 'sw', 'th', 'tr', 'tw', 'wh', 'wr']
    consonants = consonant_letters + consonant_pairs

    vowel_letters = ["a", "e", "i", "o", "u"]
    vowel_pairs = ['ai', 'au', 'ea', 'ee', 'ei', 'eu', 'ie', 'oa', 'oo', 'ou', 'ue', 'ui']

    vowels = vowel_letters + vowel_pairs
    password = ""
    while len(password) <= 25:
        syllable = random.choice(consonants) + random.choice(vowels)+random.choice(consonant_letters) + '_'
        password += syllable

    return password[:-1]


def binary_search(array, item, key = lambda x:x, strict = False):
    middle = math.floor(len(array) / 2)

    if len(array) == 0:
        if not strict:
            return -1
        else: raise ValueError("Value not found in array")


    elif key(array[middle]) == item:
        return middle

    elif key(array[middle]) > item:
        return binary_search(array[:middle], item, key, strict)

    elif key(array[middle]) < item:
        return middle+1 + binary_search(array[middle+1:], item, key, strict)

def binary_search_value(array, item, key = lambda x:x, strict = False):
    return array[binary_search(array, item, key, strict)]

def linear_search(array, item, key = lambda x:x):
    for i, val in enumerate(array):
        if key(val) == item: return i
    else:
        raise ValueError("Value not found in array")

def linear_search_value(array, item, key = lambda x:x):
    return array[linear_search(array, item, key)]

def mixed_search(array, item, prefix_len, key = lambda x:x):
    try:
        binary_search(array[:prefix_len], item, key, strict = True)
    except ValueError:
        linear_search(array[prefix_len:], item, key)


def mixed_search_value(array, item, prefix_len, key = lambda x:x):
    return array[mixed_search(array, item, prefix_len, key)]


def bubble_sort(array, key = lambda x:x, max_passes = None):

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
            if key(array[j]) < key(array[j-1]):
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
        else: print(array[ind])




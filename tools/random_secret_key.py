import random
import string


def get_secret_key(length=10):
    num_count = random.randint(1, length - 1)
    letter_count = length - num_count
    num_list = [random.choice(string.digits) for _ in range(num_count)]
    letter_list = [random.choice(string.ascii_letters) for _ in range(letter_count)]
    all_list = num_list + letter_list
    random.shuffle(all_list)
    result = "".join([i for i in all_list])
    return result

import random


def card_number_generator():

    card_number = "".join([str(random.randint(0, 9)) for _ in range(16)])
    return card_number

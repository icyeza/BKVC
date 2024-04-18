import random


def otp_code_generator():
    """This function generates Otp codes"""
    code = "".join([str(random.randint(0, 9)) for _ in range(4)])
    return code

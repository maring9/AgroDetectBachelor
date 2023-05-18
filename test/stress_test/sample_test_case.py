import random
import os
import base64

# Not used as Artillery uses NodeJS for custom functions
def sample_test_case():
    images_paths = os.listdir('test_cases')

    # Get the number of items in the test_case_list
    count = len(images_paths)

    # Get a random int between 0 and the length of test_case_list_length
    random_sample_idx = random.randint(0, count)

    sample_path = os.path.join('test_cases', images_paths[random_sample_idx])

    with open(sample_path, "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read())
      encoded_string = encoded_string.decode('utf-8')

    return encoded_string


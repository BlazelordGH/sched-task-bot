import json


def read_token(directory):
    with open(directory, mode='r') as token_file:
        token = json.load(token_file)['token']
    return token


if __name__ == '__main__':
    print("Файл должен быть импортирован")

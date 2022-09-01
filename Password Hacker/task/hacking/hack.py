import argparse
import socket
import itertools

parser = argparse.ArgumentParser()
parser.add_argument("ip")
parser.add_argument("port")
args = parser.parse_args()

chars = list(map(lambda x: chr(x), range(ord('a'), ord('z') + 1)))
nums = list(map(lambda x: chr(x), range(ord('0'), ord('9') + 1)))
alfanum = chars + nums


def password_gen():
    for num in range(1, len(alfanum) + 1):
        for password in itertools.combinations(alfanum, num):
            password = ''.join(letter for letter in password)
            yield password


with socket.socket() as client_socket:
    address = (args.ip, int(args.port))
    client_socket.connect(address)
    for password_guess in password_gen():
        client_socket.send(password_guess.encode())
        response = client_socket.recv(1024).decode()
        if response == 'Connection success!':
            print(password_guess)
            break

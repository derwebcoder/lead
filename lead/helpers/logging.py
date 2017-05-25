
import sys

def log(message="Message not defined"):
    __print("INFO  | " + message)

def log_error(message="Error not defined"):
    __print("ERROR | " + message)

def __print(message=""):
    print()
    print("==============================")
    print()
    print(message)
    print()
    print("==============================")
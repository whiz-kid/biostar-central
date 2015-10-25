"""
This file must remain Python 2.7 compatible to allow imports from Biostar 2.
"""
import time, base64, hashlib, binascii, hmac, json, logging, uuid
from django.contrib import messages


def info(request, text):
    messages.add_message(request, messages.INFO, text)


def error(request, text):
    messages.add_message(request, messages.ERROR, text)


def encrypt(text):
    tt = bytes(text, "utf-8")
    st = b"https://docs.python.org/3/library/hashlib.html"
    dk = hashlib.pbkdf2_hmac('sha256', tt, st, 100000)
    dg = binascii.hexlify(dk)
    return dg.decode("utf-8")


def get_uuid():
     return str(uuid.uuid4())
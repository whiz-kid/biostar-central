"""
This file must remain Python 2.7 compatible to allow imports from Biostar 2.
"""
import time, base64, hashlib, binascii, hmac, json, logging, uuid
from django.contrib import messages
from django.utils import timezone


def now():
    return timezone.now()


def parse_tags(text):
    "Parses tags as comma or space separated"

    # Figure out split character.
    tags = text.split(",")
    if len(tags) == 1:
        tags = text.split()
    tags = [t.strip()[:12] for t in tags]
    tags = filter(None, tags)
    # Fix tag case.
    def fixcase(x):
        return x.lower() if len(x) > 1 else x.upper()

    tags = list(map(fixcase, tags))
    return tags


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

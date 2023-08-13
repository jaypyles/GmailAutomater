# STL
import re
from email.header import decode_header


def decode_email_from(header):
    if isinstance(header, list):
        decoded_header = str(decode_header(header)[1][0])
        print("Decoded header:", decoded_header)
        email_address = re.search(r"<(.*?)>", decoded_header)[1]
    else:
        email_address = re.search(r"<(.*?)>", str(header))[1]
    return email_address

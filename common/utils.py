"""Common elements to be used throught the project."""
import hashlib

secret_key = "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZWQyNTUxOQAAACCQcN775SDLvNoGp+V80GxVFe5D22mEPotbfs5u7CGVGgAAAJg54EI7OeBCOwAAAAtzc2gtZWQyNTUxOQAAACCQcN775SDLvNoGp+V80GxVFe5D22mEPotbfs5u7CGVGgAAAEACNR2efACy2PGTbX3VUcdC07hIld5OIUo3ZNnvEexYcpBw3vvlIMu82gan5XzQbFUV7kPbaYQ+i1t+zm7sIZUaAAAAFXJpc2hpa2VzaHZnQGdtYWlsLmNvbQ=="  # noqa


def hash_generate(string, secret=secret_key):
    """Used to generated hash for the input.

    Arguments:
        string {[type]} -- The input which needs to be hashed.

    Keyword Arguments:
        secret {[type]} -- Key used to hash

    Returns:
        calculated_hash[hash] -- The hashed result
    """
    to_be_hashed = (string.replace(" ", "")) + secret
    calculated_hash = hashlib.sha256(to_be_hashed.encode("utf-8")).hexdigest()
    return calculated_hash


def check_headers(db_headers, request_headers):
    """Method to verify if request headers are same as db headers.

    Arguments:
        db_headers {dict} -- headers stored in db
        request_headers {dict} -- headers got from request.

    Returns:
        flag [bool] -- True if matches, False if fails
    """
    db_keys = []
    flag = True
    for i in db_headers.keys():
        db_keys.append(i)
    for i in db_keys:
        if flag:
            if i in request_headers:
                if str(request_headers[i]) == str(db_headers[i]):
                    flag = True
                else:
                    flag = False
            else:
                return False
        else:
            return False
    return flag

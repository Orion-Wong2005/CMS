import hashlib

def md5_encrypt(password: str) -> str:
    """MD5 32位小写加密"""
    return hashlib.md5(password.encode('utf-8')).hexdigest().lower()

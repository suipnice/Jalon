# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import base64
import os


def encodeTexte(chemin, texte):
    # the block size for the cipher object; must be 16, 24, or 32 for AES
    BLOCK_SIZE = 32

    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING = '{'

    # one-liner to sufficiently pad the text to be encrypted
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

    # one-liners to encrypt/encode and decrypt/decode a string
    # encrypt with AES, encode with base64
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))

    # generate a random secret key
    try:
        file = open(chemin, "rb")
        secret = file.read()
    except IOError:
        os.open(chemin, os.O_CREAT)
        file = open(chemin, "wb")
        secret = os.urandom(BLOCK_SIZE)
        file.write(secret)
    file.close()

    # create a cipher object using the random secret
    cipher = AES.new(secret)

    # encode a string
    #print 'Encrypted string:', EncodeAES(cipher, texte)
    return EncodeAES(cipher, texte)


def decodeTexte(texte):
    # the block size for the cipher object; must be 16, 24, or 32 for AES
    BLOCK_SIZE = 32

    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING = '{'

    # one-liners to encrypt/encode and decrypt/decode a string
    # encrypt with AES, encode with base64
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

    # generate a random secret key
    try:
        file = open("/Users/firos/Desktop/Formations/secretsecret", "rb")
        secret = file.read()
    except IOError:
        os.open("/Users/firos/Desktop/Formations/secret", os.O_CREAT)
        file = open("/Users/firos/Desktop/Formations/secret", "wb")
        secret = os.urandom(BLOCK_SIZE)
        file.write(secret)
    file.close()

    # create a cipher object using the random secret
    cipher = AES.new(secret)

    # decode the encoded string
    #print 'Decrypted string:', DecodeAES(cipher, encoded)
    return DecodeAES(cipher, texte)

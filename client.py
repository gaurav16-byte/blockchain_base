#IMPORT NECESSARY MODULES
import functions
import socket
import sqlite3
import hashlib
import os
from random import randint
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime

#TO SET THE ROOT PATH AS CURRENT FOLDER
path = os.getcwd()
os.chdir(path)

functions.cli()

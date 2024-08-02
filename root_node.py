#IMPORT NECESSARY MODULES
import functions
import socket
import sqlite3
import hashlib
import os
from random import randint
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
'''
???????????????????????????????
???????????????????????????????
???????????REDACTED????????????
???????????????????????????????
???????????????????????????????
'''

#TO SET THE ROOT PATH AS CURRENT FOLDER
path = os.getcwd()
os.chdir(path)

#CHECK FOR THE EXISTENCE OF PEER_TABLE DATABASE, CREATE IF NOT PRESENT
functions.database()
#TO CREATE THE BLOCKS FOLDER
functions.folder()
#TO GENERATE UUID OF THE USER
uid = hashlib.sha256(functions.mobo().encode('utf-8')).hexdigest()
#INCREMENT BLOCK NUMBER EVERY 10 MINUTES (1 HOUR IF LESS ACTIVITY)
current_block = 1
#THE HASH OF THE CURRENT BLOCK
block_hash = hashlib.sha256(str(current_block).encode('utf-8')).hexdigest()
#TO GET THE IP ADDRESS FOR P2P CONNECTION
ip = functions.get_internal_ip()
#SELECT A RANDOM PORT THAT WILL ALLOW TO LISTEN AND BIND CONNECT
port = randint(1025, 65535)
#SET USERNAME AS ROOT FOR THE ROOT NODE
user = 'root'
#GENERATE AN RSA KEY PAIR, SERIALIZED THEM INTO PEM FORMAT
public_key_pem, private_key_pem = functions.asymmetric()
#SHA256 HASH OF THE PUBLIC KEY
'''
???????????????????????????????
???????????????????????????????
???????????REDACTED????????????
???????????????????????????????
???????????????????????????????
'''
#ADD INITITAL VALUES TO THE DB
functions.block_log(current_block, 'root', 'root', "new block created", block_hash)
current_block, block_hash = functions.block_height(current_block, block_hash)

print('#### ROOT NODE ####')
print(f'[+]{ip}')
print(f"[+]First block created at {functions.current_time()}")
print(f"[+]Current Block:{current_block}")
print(f"[+]Previous Block Hash: {block_hash}")
print('\r')
functions.start_server(user, current_block, port, block_hash)

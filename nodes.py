#IMPORT NECESSARY MODULES
import uuid
import threading
import functions
import hashlib
import socket
import os
import sys
import sqlite3
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime
import time

def new_node():
    os.mkdir(os.environ['HOME'] + '/.confid')
    path = os.getcwd()
    os.chdir(path)  
    #TO CREATE THE BLOCKS FOLDER
    functions.folder()
    #TO GET THE IP ADDRESS FOR P2P CONNECTION
    ip = functions.get_internal_ip()
    #TO GENERATE UUID OF THE USER
    uid = hashlib.sha256(functions.mobo(ip).encode('utf-8')).hexdigest()
    #SELECT A RANDOM PORT THAT WILL ALLOW TO LISTEN AND BIND CONNECT
    port = 40000
    #SET USERNAME AS ROOT FOR THE ROOT NODE
    user = functions.username()
    #GENERATE AN RSA KEY PAIR, SERIALIZED THEM INTO PEM FORMAT
    public_key_pem, private_key_pem = functions.asymmetric()
    #TO STORE THE PRIVATE KEY
    functions.store_private_in_pem(private_key_pem)
    #TO LOAD THE PRIVATE KEY FROM PEM FORMAT
    functions.load_private_from_pem(private_key_pem)
    #SET CURRENT_BLOCK
    current_block = 1
    block_hash = hashlib.sha256(str(current_block).encode('utf-8')).hexdigest()
    t = functions.create_block(user, current_block, block_hash)
    functions.block_log(current_block, user, user, "new block created", block_hash)
    current_block, block_hash = functions.block_height(user, current_block, block_hash)
    
    #ADD VALUES TO THE DATABASE
    functions.to_peer(uid, user, public_key_pem, ip, port)
    ##ADD CODE TO SEND PUBLIC HASH AND PEERTABLE TO ALL USERS FOR PROPER FUNCTIONING OF CODE, OTHERWISE IT WOULD NOT WORK LIKE AN ACTUAL BLOCKCHAIN!!!!!!
    except_me = functions.current_users()
    for i in except_me:
        if i == user:
            pass
        else:
            x = functions.details(i)
            public_hash_receiver = x[2]
            ip_receiver = x[3]
            port_receiver = x[4]
            client_socket = functions.start_client(ip_receiver, port_receiver)
            functions.send_file(client_socket, path + '/peer_table.db')
            time.sleep(0.5)
            functions.send_message(client_socket, public_hash_receiver, '!exit')
    print(f'#### {user} NODE ####')
    print(f'[+]{ip}')
    threads = []
    for i in range(16):
        thread = threading.Thread(target=functions.start_server, args=(user, current_block, 40000 + i, block_hash))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    
def old_node(user, public_key_pem, host, port, block_hash):
    global current_block
    #TO READ THE PRIVATE KEY
    private_key_pem = functions.read_private()
    #TO LOAD PRIVATE KEY FROM .PEM FORMAT
    private_key = functions.load_private_from_pem(private_key_pem)
    #TO GET BLOCK VALUE
    files = os.listdir(path + "/blocks/")
    for i in range(len(files)):
        files[i] = int(files[i][:files[i].find('.')])
    current_block = files[-1]
    functions.block_log(current_block, user, user, f'{user} logged back in', block_hash)
    current_block, block_hash = functions.block_height(user, current_block, block_hash)
    
    print(f'#### {user} NODE ####')
    print(f'[+]{host}')
    threads = []
    for i in range(16):
        thread = threading.Thread(target=functions.start_server, args=(user, current_block, 40000 + i, block_hash))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

#TO SET THE ROOT PATH AS CURRENT FOLDER
path = os.getcwd()
os.chdir(path)

uid = hashlib.sha256(functions.mobo(functions.get_internal_ip()).encode('utf-8')).hexdigest()
uuids = []
conn = sqlite3.connect('peer_table.db')
cur = conn.cursor()
for i in cur.execute('SELECT uuid FROM NODES'):
    uuids.append(i[0])
if uid in uuids:
    for i in cur.execute(f'SELECT * FROM NODES WHERE uuid="{uid}"'):
        user = i
    conn.close()
    detail = functions.details(user[1])
    user = detail[1]
    public_key_pem = detail[2]
    host = detail[3]
    port = detail[4]
    print(f"[+]WELCOME BACK {detail[1]}")
    files = os.listdir(path + "/blocks/")
    for i in range(len(files)):
        files[i] = int(files[i][:files[i].find('.')])
    last_block = str(files[-1]) + '.db'
    block_conn = sqlite3.connect(f"blocks/{last_block}")
    cursor = block_conn.cursor()
    hashes = []
    for i in cursor.execute('SELECT hash FROM LOGS'):
        hashes.append(i[0])
    block_hash = hashes[-1]
        
    old_node(user, public_key_pem, host, port, block_hash)
else:
    new_node()

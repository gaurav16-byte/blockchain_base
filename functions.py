#IMPORT NECESSARY MODULES
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
import uuid

#TO SET THE ROOT PATH AS CURRENT FOLDER
path = os.getcwd()
os.chdir(path)

#USAGE DOCUMENTATION
def doc():
    print('''    help h or ? - To open documentation
    lu - To list all the users on the chain
    connect - To connect to another node (specify username)
    sm or send_message - To send a text message
    sf or send_file - To send a file (.txt, .jpg, .exe) etc.
    !exit - to terminate connection from node

    Usage: ? or h or help - only for opening the documentation
    Usage: connect [username]
           [function] [filepath]/[message in inverted commas]

    Ex. ::> connect root (connects to user root)
        ::> sf C:\\absolute\\path\\to\\the\\file.extension (sends file)
        ::> sm this is a message (sends message)
        ::> lu''')

#CHECK FOR THE EXISTENCE OF PEER_TABLE DATABASE, CREATE IF NOT PRESENT
def database():
    if 'peer_table.db' not in os.listdir(path + '\\'):
        conn = sqlite3.connect('peer_table.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE NODES(uuid text, username text, public_key text, ip_addr text, port integer)')
        conn.commit()
        conn.close()
    else:
        pass

#TO CREATE THE BLOCKS FOLDER
def folder():
    if 'blocks' not in os.listdir(path + '\\'):
        os.mkdir(f"{path}\\blocks")
    else:
        pass

#TO GENERATE DEVICE SPECIFIC UID
def mobo(ip):
    namespace = uuid.NAMESPACE_DNS
    return str(uuid.uuid5(namespace, ip)).replace('-','')

#TO GET THE IP ADDRESS FOR P2P CONNECTION
def get_internal_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal_ip = s.getsockname()[0]
        s.close()
        return internal_ip
    except Exception as e:
        return str(e)

#TO ASSIGN USERNAMES TO THE NODES
def username():
    users = []
    conn = sqlite3.connect('peer_table.db')
    cur = conn.cursor()
    for i in cur.execute('SELECT username FROM NODES'):
        users.append(i[0])
    conn.close()

    user = input("Enter Username: ")
    while user in users:
        print("[-]Username already exists!")
        user = input("Enter Username: ")
    else:
        print("[+]USERNAME ASSIGNED")
        return user

#ADD VALUES TO THE PEER TABLE
def to_peer(uid, user, public_hash, ip, port):
    conn = sqlite3.connect('peer_table.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO NODES VALUES(?, ?, ?, ?, ?)', [uid, user, public_hash, ip, port])
    conn.commit()
    conn.close()

#TO GENERATE AN ASYMMETRIC KEY-PAIR
def asymmetric():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend = default_backend()
    )
    public_key = private_key.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return public_key_pem, private_key_pem

#TO LOAD THE PUBLIC KEY FROM PEM FORMAT
def load_public_from_pem(public_key_pem):
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend()
    )

    return public_key

#TO LOAD THE PRIVATE KEY FROM PEM FORMAT
def load_private_from_pem(private_key_pem):
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,  #We didn't set a password
        backend=default_backend()
    )

    return private_key

#TO ENCRYPT MESSAGES USING PUBLIC_KEY
def encrypt(message, public_key):   #MESSAGE TO BE IN BYTES
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return ciphertext

#TO DECRYPT CIPHERTEXT USING PRIVATE_KEY
def decrypt(ciphertext, private_key):
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return plaintext

#TO STORE THE PUBLIC_KEY IN PEM FORMAT (IN THE OPEN)
def store_public_in_pem(public_key_pem):
    public_hash = hashlib.sha256(public_key_pem).hexdigest()
    with open(public_hash + '.pem', 'wb') as public_key_file:
        public_key_file.write(public_key_pem)

#TO STORE THE PRIVATE_KEY IN PEM FORMAT (HIDDEN)
def store_private_in_pem(private_key_pem):
    with open(os.environ['HOME'] + '\\' + 'private_key.pem', 'wb') as private_key_file:
        private_key_file.write(private_key_pem)

#TO READ THE PUBLIC_KEY INTO PEM FORMAT FROM .PEM FILE
def read_public(public_hash):
    with open(public_hash + '.pem', 'rb') as public_key_file:
        public_key_pem = public_key_file.read()

    return public_key_pem

#TO READ THE PRIVATE_KEY INTO PEM FORMAT FROM .PEM FILE
def read_private():
    with open(os.environ['HOME'] + '\\' + 'private_key.pem', 'rb') as private_key_file:
        private_key_pem = private_key_file.read()

    return private_key_pem

#TO GET THE CURRENT TIME
def current_time():
    t = datetime.now()
    jetzt = f"{t.hour}:{t.minute}:{t.second} {t.day}-{t.month}-{t.year} IST"
    return jetzt

#TO GET A LIST OF ALL THE CURRENT USERS
def current_users():
    users = []
    conn = sqlite3.connect('peer_table.db')
    cur = conn.cursor()
    for i in cur.execute('SELECT username FROM NODES'):
        users.append(i[0])
    conn.close()

    return users

#TO GET DETAILS ABOUT A USER
def details(user):
    users = current_users()
    if user not in users:
        return False
    else:
        conn = sqlite3.connect('peer_table.db')
        cur = conn.cursor()
        for i in cur.execute(f'SELECT * FROM NODES WHERE username="{user}"'):
            detail = i
        conn.close()

    return detail

#TO CREATE NEW BLOCKS
def create_block(user, current_block, block_hash):
    t = current_time()
    block_conn = sqlite3.connect(f"blocks\\{current_block}.db")
    cursor = block_conn.cursor()
    cursor.execute('CREATE TABLE LOGS(sender text, receiver text, activity text, timestamp text, hash text)')
    cursor.execute('INSERT INTO LOGS VALUES(?, ?, ?, ?, ?)', [user, user, "new block created", t, block_hash])
    block_conn.commit()
    block_conn.close()
    return t

#CREATE NEW BLOCK AFTER 100 ENTRIES
def block_height(user, current_block, block_hash):
    block_conn = sqlite3.connect(f"blocks\\{current_block}.db")
    cursor = block_conn.cursor()
    for i in cursor.execute('SELECT COUNT(*) FROM LOGS'):
        count = i[0]
    block_conn.close()
    if count > 99:
        has = merkel(current_block, block_hash)     #NEW BLOCK HASH
        current_block += 1
        t = create_block(user, current_block, block_hash)
        block_log(current_block, user, user, "New block created", block_hash)
        print("[+] NEW BLOCK CREATED")
        print(f"[+] CURRENT BLOCK: f{current_block}")
        print(f"[ CURRENT BLOCK HASH: {has}]")
        print(f"Block created at: {t}")
        return current_block, has
    else:
        return current_block, block_hash

#TO LOG DATA INTO BLOCKS
def block_log(current_block, sender, receiver, activity, block_hash):
    block_conn = sqlite3.connect(f"blocks\\{current_block}.db")
    cursor = block_conn.cursor()
    cursor.execute('INSERT INTO LOGS VALUES(?, ?, ?, ?, ?)', [sender, receiver, activity, current_time(), block_hash])
    block_conn.commit()
    block_conn.close()

#TO RETURN THE MERKEL ROOT HASH OF THE CURRENT BLOCK
def merkel(current_block, block_hash):
    block_conn = sqlite3.connect(f"blocks\\{current_block}.db")
    cursor = block_conn.cursor()
    logs = []
    for i in cursor.execute('SELECT * FROM LOGS'):
        logs.append(i)
    hashes = []
    for i in logs:
        hashes.append(hashlib.sha256(i[0].encode('utf-8') + i[1].encode('utf-8') + i[2].encode('utf-8') + i[3].encode('utf-8') + i[4].encode('utf-8')).hexdigest())

    hashes.append(block_hash)
    while len(hashes) > 1:
        hashes.append(hashlib.sha256(hashes[0] + hashes[1]).hexdigest())
        hashes.pop(0); hashes.pop(0)

    return hashes

#TO FIND THE HASH OF THE BLOCK
def prev_block_hash(block_hash, t, merkel):
    hashed_t = hashlib.sha256(t.encode('utf-8')).hexdigest()
    return hashlib.sha256((block_hash + hashed_t + merkel).encode('utf-8')).hexdigest()

#TO SEND MESSAGES
def send_message(client_socket, public_key_pem, message):
    if message == '!exit':
        client_socket.send('exit'.encode('utf-8'))
        print("[-]CONNECTION TERMINATED")
        return True
    else:
        public_key = load_public_from_pem(public_key_pem)
        mess = message.encode('utf-8')
        msg = encrypt(mess, public_key)
        client_socket.send(msg)
        print('[+]MESSAGE SENT SUCCESSFULLY')
        return False

#TO SEND FILE
def send_file(client_socket, filepath):
    file = open(filepath, 'rb')
    file_binary = file.read()
    message = filepath[filepath.rfind('\\') + 1:].encode('utf-8') + ':::::'.encode('utf-8') + file_binary
    client_socket.send(message)
    print('[+]FILE SENT SUCCESSFULLY')

#TO START THE CONNECTION
def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

#TO GET THE SENDER DETAILS
def from_ip(ip):
    conn = sqlite3.connect('peer_table.db')
    cursor = conn.cursor()
    for i in cursor.execute(f'SELECT username FROM NODES WHERE ip_addr="{ip}"'):
        sender = i[0]
    return sender

#TO START THE LISTENER
def start_server(user, current_block, port, block_hash):
    host = '0.0.0.0'  # Use 0.0.0.0 to bind to all available interfaces
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #TO ALLOW PORT REUSE
    server_socket.bind((host, port))
    server_socket.listen(5)  # Allow five connections

    print(f"[+]Server listening on {host}:{port}")

    conn, addr = server_socket.accept()     #To accept incoming connection
    #This part displays the node name if it exists otherwise displays the ip of the new node
    ips = []
    sconn = sqlite3.connect('peer_table.db')
    cur = sconn.cursor()
    for i in cur.execute('SELECT ip_addr FROM NODES'):
        ips.append(i[0])
    if addr[0] not in ips:
        sender = addr[0]
    else:
        for i in cur.execute(f'SELECT username FROM NODES WHERE ip_addr="{addr[0]}"'):
            sender = i[0]
    sconn.close()

    print(f"[+]CONNECTION FROM {addr}")
    block_log(current_block, sender, user, f"Connection from {sender}", block_hash) #Log the incoming connection
    current_block, block_hash = block_height(user, current_block, block_hash) #Check whether the block size has reached the threshold

    while True:
        data = conn.recv(209715200)     #Can receive 200MB of data
        if not data:
            break
        elif data.find(':::::'.encode('utf-8')) > -1:           #Check whether : exists, else it's a message
            filename = data[:data.find(':::::'.encode('utf-8'))].decode('utf-8')
            file = data[data.rfind(':::::'.encode('utf-8')) + 5:]
            f = open(filename, 'wb')
            f.write(file)
            f.close()
            print(f"[+]Received file: {filename}")
            block_log(current_block, sender, user, f"Received file {filename}", block_hash)
            current_block, block_hash = block_height(user, current_block, block_hash)
        elif data == b'exit':                               #checks whether the sender wishes to terminate the connection
            conn.close()
            print("[-]CONNECTION TERMINATED FROM REMOTE HOST")
            break
        else:                                               #to accept incoming message
            private_key_pem = read_private()
            private_key = load_private_from_pem(private_key_pem)
            plaintext = decrypt(data, private_key)
            print(f"[+]Received message: {plaintext.decode('utf-8')}")
            block_log(current_block, sender, user, "Message received", block_hash)
            current_block, block_hash = block_height(user, current_block, block_hash)

    server_socket.close()                                   #Restart server after data sharing is complete to refresh memory
    start_server(user, current_block, port, block_hash)

#TO RUN THE COMMAND LINE FOR RUNNING THE CLIENT
def cli():
    option = input("::> ")
    try:
        option, user = option.split()
    except Exception:
        while option.lower() not in ['lu', 'help', 'h', '?']:
            print('[-]Invalid option!, Refer docs with h or ?')
            option = input("::> ")
    else:
        if len(option.lower()) > 4 and option.lower() == 'connect': #This loop connects to target node
            x = details(user)
            if x == False:
                print("[-]Wrong Username!")
                return False
            else:
                user_name = x[1]
                public_key_pem = x[2]
                host = x[3]
                port = x[4]
                uid = hashlib.sha256(mobo(get_internal_ip()).encode('utf-8')).hexdigest()
                uuids = []
                conn = sqlite3.connect('peer_table.db')
                cur = conn.cursor()
                for i in cur.execute('SELECT uuid FROM NODES'):
                    uuids.append(i[0])
                conn.close()
                n = uuids.index(uid)
                client_socket = start_client(host, port + n)
                print(f"[+]CONNECTED TO NODE {user_name}")
                while True:
                    func = input("::> ")                            #This loop is used to perform functions
                    perform = func[:func.find(' ')]
                    rest = func[func.find(' ') + 1:]
                    while perform.lower() not in ['sm', 'sf', 'send_message', 'send_file']:
                        print("Invalid function, refer documentation?")
                        func = input("::> ")
                        perform = func[:func.find(' ')]
                        rest = func[func.find(' ') + 1:]
                    else:
                        if perform.lower() in ['sm', 'send_message']:
                            if send_message(client_socket, public_key_pem, rest): #If termination condition true, conn terminates
                                break
                        elif perform.lower() in ['sf', 'send_file']:
                            send_file(client_socket, rest)

        elif option.lower() in ['h', '?', 'help']:
            doc()
        elif option.lower() in 'lu':
            users = current_users()
            for i in users:
                print(i, end = ', ')

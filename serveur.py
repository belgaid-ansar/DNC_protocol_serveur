from ast import List
import socket
import threading
import sys
import re

Users = {}

#METHODE valide_commande
def match_commande(socket,commande):
    if re.match(r"CONNECT .+", commande) or  re.match(r"USERS", commande) or  re.match(r"RENAME .+", commande) :
        return True
    else :
        socket.sendall("402".encode())
        return False
#FIN METHODE

#METHODE CONNECTED:
def connect(socket,message): 
    
    if not re.match(r"CONNECT [a-zA-Z]+", message):  # On verifie l'orthographe du username
        socket.sendall("407".encode())
        return ""
    else:
        x = message.split(" ")  # On recupere le username
        username = x[1]
        
        if username in Users:   # Verification du username
            socket.sendall("406".encode())
            return ""
        else:
            print(username, "connected to the server")
            #io.emit('message', "this is a test");
            socket.sendall("200".encode())  # je renvoie le code de retour

            Users[username] = {}  # Ajout de l'utilisateur
            Users[username]['port'] = socket
            return username
            
#FIN METHODE

#METHODE RENAME:
def rename(socket,message,username):

    if not re.match(r"RENAME [a-zA-Z]+", message) :
            socket.sendall("207".encode())
            return ""
    else :
        y = message.split(" ") # On recupere le username
        new_username=y[1]
        
        if new_username in Users :  # Verification du username
            socket.sendall("406".encode())
            return ""
        else :
            Users[new_username] = Users.pop(username)
            socket.sendall("203".encode())

            for value in Users.values() :   # prevenir les autres clients
                if Users[new_username]['port'] != value['port'] :
                    code = "CODE "+new_username
                    value["port"].sendall(code.encode())

        return new_username            
#FIN METHODE

# METHODE traiter_client
def traiter_client(sock_file, adr_client,username_client=None): 

    print("Serveur à l'écoute")
    message = sock_file.recv(256).decode()
    
    while not match_commande(sock_file,message) :
        print("Serveur à l'écoute")
        message = sock_file.recv(256).decode()
    
    CONNECTED =False
    while not CONNECTED:
        username=connect(sock_file,message)
        if username != "":
            username_client = username
            CONNECTED=True
        else:
            print("Serveur à l'écoute")
            message = sock_file.recv(256).decode()
        
    while CONNECTED:  # On traite les autres commandes apres la commande CONNECT

        print("Serveur à l'écoute")
        message = sock_file.recv(256).decode() 

        while not match_commande(sock_file,message) :
            print("Serveur à l'écoute")
            message = sock_file.recv(256).decode()
        
        if re.match(r"CONNECT [a-zA-Z]+", message):
            sock_file.sendall("418".encode())

        elif message == "USERS":
            sock_file.sendall(("200 "+" , ".join(list(Users.keys()))).encode())

        elif re.match(r"RENAME .+", message):
            val=rename(sock_file,message,username_client)
            if val != "" :
                username_client = val       
# FIN METHODE 

#Arguments
if len(sys.argv) != 2:
	print(f"Usage: {sys.argv[0]} <port>", file=sys.stderr)
	sys.exit(1)

sock_locale= socket.socket()
sock_locale.bind(("", int(sys.argv[1])))
sock_locale.listen(4)

print("Serveur en attente sur le port " + sys.argv[1], file=sys.stderr)

while True:
    try:
        sock_client, adr_client = sock_locale.accept()
        threading.Thread(target=traiter_client, args = (sock_client, adr_client)).start()
    except KeyboardInterrupt:
        break

sock_locale.shutdown(socket.SHUT_RDWR)
print("Bye")

for t in threading.enumerate():
    if t != threading.main_thread(): 
        t.join
        print("Arret du serveur", file=sys.stderr)

sys.exit(0)

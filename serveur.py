import socket
import threading
import sys
import re

Users = {}

#METHODE valide_commande
def valide_commande(commande):
    if commande :
        pass
#FIN METHODE

# METHODE traiter_client
def traiter_client(sock_file, adr_client):
    CONNECTED = False

    #Traitement de la commande CONNECT
    print("Serveur à l'écoute")
    mess = sock_file.recv(256)
    while not CONNECTED :
        while not re.match(r"CONNECT .+", mess.decode()): #Tant qu'il n'est pas connecté
            sock_file.sendall("402".encode())
            mess = sock_file.recv(256)

        while not re.match(r"CONNECT [a-zA-Z]+", mess.decode()): #Tant qu'il n'est pas connecté
            sock_file.sendall("407".encode())
            mess = sock_file.recv(256) 

        x = mess.decode().split(" ") #On recupere le username
        username= x[1]
        #print("bonjour")
        #Verification du username
        if username in Users :
            sock_file.sendall("406".encode())
            mess = sock_file.recv(256)
        else :
            print(username,"connected to the server")
            #io.emit('message', "this is a test");
            sock_file.sendall("200".encode()) # je renvoie le code de retour 

            #Ajout de l'utilisateur
            Users[username]={}
            Users[username]['port']= adr_client
       
            CONNECTED = True

    while True and CONNECTED == True:
        print("Serveur à l'écoute")
        mess = sock_file.recv(256)

        #On traite les autres commandes apres la commande CONNECT      
        if re.match(r"CONNECT [a-zA-Z]+", mess.decode()):
            sock_file.sendall("418".encode())

        elif mess.decode() == "USERS":
            sock_file.sendall(("200 "+str(Users)).encode())

        elif re.match(r"RENAME .+", mess.decode()):
            if not re.match(r"RENAME [a-zA-Z]+", mess.decode()) :
                sock_file.sendall("207".encode())
            else :
                new_username = mess.decode().split(" ") #On recupere le username
                #Verification du username
                if new_username[1] in Users :
                    sock_file.sendall("406".encode())
                else :
                    Users[new_username[1]] = Users.pop(username)
                    sock_file.sendall("203".encode())

        elif mess.decode() == "QUIT" :
            pass

        elif mess.decode() == "" :
            pass

        else: 
            sock_file.sendall("402".encode())
            
            '''
            elif mess.decode()=="QUIT":
                sock_locale.shutdown(socket.SHUT_RDWR)
                print("Bye")
            '''

        #sock_file.sendall(mess.upper())

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

import socket
import threading
import sys
import re

Users = {}
nb_user=0

#METHODE valide_commande
def valide_commande(commande):
    if commande :
        pass
#FIN METHODE

# METHODE traiter_client
def traiter_client(sock_file, adr_client, nb_user):

    #Traitement de la commande CONNECT
    print("Serveur à l'écoute")
    mess = sock_file.recv(256)
    while not re.match(r"CONNECT [a-zA-Z]+", mess.decode()): #Tant qu'il n'est pas connecté
        sock_file.sendall("402".encode())
        mess = sock_file.recv(256)

    x = mess.decode().split(" ") #On recupere le username

    #Verification du username
    #.......

    print(x[1],"connected to the server")
    sock_file.sendall("200".encode()) # je renvoie le code de retour 
    
    #Creation de la liste des utilisateurs
    Users[nb_user] = {}
    Users[nb_user]['username'] = x[1]
    Users[nb_user]['port'] = adr_client

    while True:
        print("Serveur à l'écoute")
        mess = sock_file.recv(256)

        #On traite les autres commandes apres la commande CONNECT      
        if re.match(r"CONNECT [a-zA-Z]+", mess.decode()):
            sock_file.sendall("418".encode())
        elif mess.decode() == "USERS":
            sock_file.sendall(("200 "+str(Users)).encode())
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
        nb_user =nb_user+1
        threading.Thread(target=traiter_client, args = (sock_client, adr_client,nb_user)).start()
    except KeyboardInterrupt:
        break

sock_locale.shutdown(socket.SHUT_RDWR)
print("Bye")

for t in threading.enumerate():
    if t != threading.main_thread(): 
        t.join
        print("Arret du serveur", file=sys.stderr)

sys.exit(0)

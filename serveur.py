import socket
import threading
import sys
import re

Users = {}
nb_user=0

def traiter_client(sock_file, adr_client, nb_user):
    while True:
        print("Serveur à l'écoute")
        #print(Users)
        mess = sock_file.recv(256)
        if mess.decode() == "" :
            break
        else:
            #on traite la commande CONNECT
            if re.findall("CONNECT", mess.decode()):
                x = mess.decode().split(" ")
                print(x[1],"connected to the server")
                retour_connection="200"
                sock_file.sendall(retour_connection.encode()) # je renvoie le code de retour 
                
                Users[nb_user] = {}
                Users[nb_user]['username'] = x[1]
                Users[nb_user]['port'] = adr_client
                
                #On traite les autres commandes apres la commande CONNECT
                if re.findall("CONNECT", mess.decode()):
                    retour="418"
                sock_file.sendall(retour.encode())
            '''
            elif mess.decode()=="QUIT":
                sock_locale.shutdown(socket.SHUT_RDWR)
                print("Bye")
            '''

        #sock_file.sendall(mess.upper())


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

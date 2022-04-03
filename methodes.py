from ast import List
import socket
import threading
import sys
import re

Users = {}

# METHODE traiter_client
def traiter_client(sock_fille, adr_client,username_client=None): 

    print("Serveur à l'écoute")
    message = sock_fille.recv(256).decode()
    
    while not match_commande(sock_fille,message) :
        print("Serveur à l'écoute")
        message = sock_fille.recv(256).decode()
    
    CONNECTED =False
    while not CONNECTED:
        username=connect(sock_fille,message)
        if username != "":
            username_client = username
            CONNECTED=True
        else:
            print("Serveur à l'écoute")
            message = sock_fille.recv(256).decode()
        
    while CONNECTED:  # On traite les autres commandes apres la commande CONNECT

        print("Serveur à l'écoute")
        message = sock_fille.recv(256).decode() 

        while not match_commande(sock_fille,message) :
            print("Serveur à l'écoute")
            message = sock_fille.recv(256).decode()
        
        if re.match(r"CONNECT [a-zA-Z]+", message):
            sock_fille.sendall("418".encode())

        elif message == "USERS":
            sock_fille.sendall(("200 "+" , ".join(list(Users.keys()))).encode())

        elif re.match(r"RENAME .+", message):
            val=rename(sock_fille,message,username_client)
            if val != "" :
                username_client = val  

        elif re.match(r"BROADCAST .+", message) : 
            broadcast(sock_fille,message,username_client)     

        elif message == "QUIT" :
            sock_fille.sendall("CODE je quitte".encode())
            return sock_fille.shutdown 

# FIN METHODE

#METHODE valide_commande
def match_commande(socket,commande):
    if re.match(r"CONNECT .+", commande) or  re.match(r"USERS", commande) or  re.match(r"RENAME .+", commande) or re.match(r"BROADCAST .+", commande) or re.match(r"QUIT", commande):
        return True
    else :
        socket.sendall("402".encode())
        return False
#FIN METHODE

#METHODE CONNECT:
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

            for value in Users.values() :   # prevenir les autres clients
                if Users[username]['port'] != value['port'] :
                    code = "119 "+username
                    value["port"].sendall(code.encode())

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
            #socket.sendall("203".encode())

            for value in Users.values() :   # prevenir les autres clients
                if Users[new_username]['port'] != value['port'] :
                    code = "CODE "+username+" "+new_username
                    value["port"].sendall(code.encode())
            
            socket.sendall("203".encode())

        return new_username            
#FIN METHODE

#METHODE BROADCAST :
def broadcast(socket,message,username):
    y = message.split(" ", 1) # On recupere le username
    broadcast=y[1]

    #socket.sendall("206".encode()) # message de retour a l'envoyeur

    for value in Users.values() :   # prevenir les autres clients
        if Users[username]['port'] != value['port'] :
            code = "118 "+username+" "+broadcast
            value["port"].sendall(code.encode())

    socket.sendall("206".encode()) # message de retour a l'envoyeur

    return broadcast            
#FIN METHODE
from ast import List
import socket
import threading
import sys
import re

Users = {}

# METHODE traiter_client
def traiter_client(sock_fille, adr_client,username_client=None): 

    print("Serveur à l'écoute")
    print(Users)
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

        while match_commande(sock_fille,message) == "" :
            print("Serveur à l'écoute")
            message = sock_fille.recv(256).decode()
        
        COMMANDE = match_commande(sock_fille,message) # Je recupere la commande

        if COMMANDE == "CONNECT":
            sock_fille.sendall("418".encode())

        elif COMMANDE == "USERS":
            sock_fille.sendall(("200 "+" , ".join(list(Users.keys()))).encode())

        elif COMMANDE == "RENAME":
            val=rename(sock_fille,message,username_client)
            if val != "" :
                username_client = val  

        elif COMMANDE == "BROADCAST": 
            broadcast(sock_fille,message,username_client)     
        
        elif COMMANDE == "WHISPER" : 
            whisper(sock_fille,message,username)
        
        elif COMMANDE == "ACCEPTWHISPER" : 
            acceptwhisper(sock_fille,message,username)

        elif COMMANDE == "DECLINEWHISPER" : 
            acceptwhisper(sock_fille,message,username)

        elif COMMANDE == "QUIT" :
            sock_fille.sendall("CODE je quitte".encode())
            return sock_fille.shutdown 
# FIN METHODE

#METHODE match_commande
def match_commande(socket,commande):
    if re.match(r"CONNECT .+", commande) :
        return "CONNECT"
    elif re.match(r"USERS", commande) :
        return "USERS"
    elif re.match(r"RENAME .+", commande) :
        return "RENAME"
    elif re.match(r"BROADCAST .+", commande) :
        return "BROADCAST"
    elif re.match(r"WHISPER .+", commande) :
        return "WHISPER"
    elif re.match(r"ACCEPTWHISPER .+",commande):
        return "ACCEPTWHISPER"
    elif re.match(r"DECLINEWHISPER .+",commande):
        return "DECLINEWHISPER"
    elif re.match(r"QUIT", commande) :
        return "QUIT"
    else :
        socket.sendall("402".encode())
        return ""
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
            Users[username]['chat'] = {}

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
            
            socket.sendall("203".encode()) # j'envoie la reponse au client qui vient de se renommer

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
    #return broadcast            
#FIN METHODE

#METHODE WHISPER  :
def whisper (socket,message,username):
    y = message.split(" ") # On recupere le username avec qui il veut communiquer
    username_chat=y[1]

    if username_chat not in Users:   # Verification du username : s'il n'existe pas ...
        code= "411 "+username_chat
        socket.sendall(code.encode())

    else :   
        for value in Users.values() :   
            if Users[username_chat]['port'] == value['port'] : # Je previens le client concerné qu'on desire chater avec lui 
                code = "116 "+username
                value["port"].sendall(code.encode())

            elif Users[username]['port'] == value['port'] : # J'enregistre la demande de tchat chez l'envoyeur
                Users[username]['chat'][username_chat] = False 

        socket.sendall("101".encode()) # message de retour a l'envoyeur : sa demande a été envoyé      
#FIN METHODE

#METHODE ACCEPTWHISPER user  :
def acceptwhisper (socket,message,username):
    y = message.split(" ")    # On recupere le username avec qui il va se mettre a communiquer
    username_chat_sender=y[1]

    if username_chat_sender not in Users:   # Verification du username : s'il n'existe pas ...
        code= "411 " + username_chat_sender
        socket.sendall(code.encode())
    
    else :
        if username not in Users[username_chat_sender]['chat'] :  #  je verifie si on se trouve ds les demandes de l'envoyeur
            code = "412 " + username_chat_sender
            socket.sendall(code.encode())

        else :      #  On se trouve dans les demandes de l'envoyeur  
               # On verifie qu'il n'a pas deja accepté ...
                if Users[username_chat_sender]['chat'][username] == True : # S'il a deja accepté
                    code = "415 " + username_chat_sender
                    socket.sendall(code.encode())
                    
                else :
                    Users[username_chat_sender]['chat'][username] == True
                    code = "106 " + username_chat_sender   # On previent le client qu'il vient d'accepter la demande de whisper
                    
                    for value in Users.values() :

                        if Users[username_chat_sender]['port'] == value['port'] : # Je previens le client concerné que sa demande de tchat a été acceptée  
                            code_retour = "102 "+username
                            value["port"].sendall(code_retour.encode())
                    
                    
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : il vient d'accepter la demande de whisper   
#FIN METHODE

#METHODE DECLINEWHISPER user  :
def declinewhisper (socket,message,username):
    y = message.split(" ")    # On recupere le username avec qui il va se mettre a communiquer
    username_chat_sender=y[1]

    if username_chat_sender not in Users:   # Verification du username : s'il n'existe pas ...
        code= "411 " + username_chat_sender
        socket.sendall(code.encode())
    
    else :
        if username not in Users[username_chat_sender]['chat'] :  #  je verifie si on se trouve ds les demandes de l'envoyeur
            code = "412 " + username_chat_sender
            socket.sendall(code.encode())

        else :      #  On se trouve dans les demandes de l'envoyeur  
               # On verifie qu'il n'a pas deja accepté ...
                if Users[username_chat_sender]['chat'][username] == True : # S'il a deja accepté
                    code = "415 " + username_chat_sender
                    socket.sendall(code.encode())  
                    
                else :
                    Users[username_chat_sender]['chat'][username] == True
                    code = "107 " + username_chat_sender  # On previent le client qu'il vient de refuser la demande de whisper
                    
                    for value in Users.values() :

                        if Users[username_chat_sender]['port'] == value['port'] : #  Je previens le client concerné que sa demande de tchat a été refusée 
                            code_retour = "103 "+ username
                            value["port"].sendall(code_retour.encode())
                    
                    
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : il vient de reffuser la demande de whisper    
#FIN METHODE


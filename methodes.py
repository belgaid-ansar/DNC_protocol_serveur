from ast import List
import socket
import threading
import sys
import re
import os.path

Users = {}

# METHODE traiter_client :
def traiter_client(sock_fille, adr_client,username_client=None): 

    CONNECTED = False
    MUTED = False
    
    print("Serveur à l'écoute")

    while True :

        print(Users)
        print("Serveur à l'écoute")

        try :
            message = sock_fille.recv(256).decode()
        except :   # Connexion interrompue 
            if CONNECTED :
                for value in Users.values() :  # Je supprime le client partout
                    if username in value['chat'] :  # Des chats 
                        value['chat'].pop(username)
                    if username in value['file'] :  # Des fichiers
                        value['file'].pop(username)

                Users.pop(username)  # Enfin, je supprime le client des users

            sock_fille.shutdown(socket.SHUT_RDWR)
            break
        
        COMMANDE = match_commande(sock_fille,message) # je recupere la methode

        if not CONNECTED:
            username=connect(sock_fille,message)
            if username != "":
                username_client = username
                CONNECTED=True

        elif CONNECTED and MUTED :
            
            if COMMANDE == "MUTE" :
                sock_fille.sendall("414".encode())

            elif COMMANDE == "UNMUTE" :
                unmute(sock_fille,username)
                MUTED = False
                
            else :
                sock_fille.sendall("409".encode())

        elif CONNECTED and not MUTED:  # On traite les autres commandes apres la commande CONNECT
        
            if COMMANDE != "" :
                
                if COMMANDE == "CONNECT":
                    sock_fille.sendall("418".encode())

                elif COMMANDE == "USERS":
                    sock_fille.sendall(("208 "+" ".join(list(Users.keys()))).encode())

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
                    declinewhisper(sock_fille,message,username)

                elif COMMANDE == "WHISPERMESSAGE" : 
                    whispermessage(sock_fille,message,username)

                elif COMMANDE == "ENDWHISPER" : 
                    endwhisper(sock_fille,message,username)
                
                elif COMMANDE == "SENDFILEDEMAND" : 
                    sendfiledemand(sock_fille,message,username)
                
                elif COMMANDE == "ACCEPTSENDFILE" : 
                    acceptsendfile(sock_fille,message,username)

                elif COMMANDE == "DECLINESENDFILE" : 
                    declinesendfile(sock_fille,message,username)

                elif COMMANDE == "SENDFILE" : 
                    sendfile(sock_fille,message,username)

                elif COMMANDE == "ENDSENDFILE" : 
                    endsendfile(sock_fille,message,username)

                elif COMMANDE == "MUTE" :
                    mute(sock_fille,username)
                    MUTED = True
                
                elif COMMANDE == "UNMUTE" :
                    unmute(sock_fille,username)
                    #MUTED = False
               
                elif COMMANDE == "QUIT" :
                    quit(sock_fille,username)
                    CONNECTED = False

            else :
                sock_fille.sendall("402".encode())

# FIN METHODE

'''# METHODE first_connection :
def first_connection(socket,commande):
    if re.match(r"CONNECT [^ ]+$", commande) :
        return True
    else :
        socket.sendall("402".encode())
        return False
# FIN METHODE'''

# METHODE match_commande :
def match_commande(socket,commande):
    if re.match(r"CONNECT [^ ]+$", commande) :
        return "CONNECT"
    elif re.match(r"USERS", commande) :
        return "USERS"
    elif re.match(r"RENAME [^ ]+$", commande) :
        return "RENAME"
    elif re.match(r"BROADCAST .+", commande) :
        return "BROADCAST"
    elif re.match(r"WHISPER [^ ]+$", commande) :
        return "WHISPER"
    elif re.match(r"ACCEPTWHISPER [^ ]+$",commande):
        return "ACCEPTWHISPER"
    elif re.match(r"DECLINEWHISPER [^ ]+$",commande):
        return "DECLINEWHISPER"
    elif re.match(r"WHISPERMESSAGE [^ ]+ .+",commande):
        return "WHISPERMESSAGE"
    elif re.match(r"ENDWHISPER [^ ]+$",commande):
        return "ENDWHISPER"
    elif re.match(r"SENDFILEDEMAND [^ ]+$",commande):
        return "SENDFILEDEMAND"
    elif re.match(r"ACCEPTSENDFILE [^ ]+ [^ ]+$",commande):
        return "ACCEPTSENDFILE"
    elif re.match(r"DECLINESENDFILE [^ ]+$",commande):
            return "DECLINESENDFILE"
    elif re.match(r"SENDFILE [^ ]+ [^ ]+$",commande):
        return "SENDFILE"
    elif re.match(r"ENDSENDFILE [^ ]+$",commande):
        return "ENDSENDFILE"
    elif re.match(r"^MUTE$",commande):
        return "MUTE"
    elif re.match(r"^UNMUTE$",commande):
        return "UNMUTE"
    elif re.match(r"QUIT", commande) :
        return "QUIT"
    else :
        return ""
# FIN METHODE

# METHODE QUIT
def quit(socket,username):

    for value in Users.values() : 
        # prevenir les autres clients
        code = "121 "+username  
        value["port"].sendall(code.encode())

        # Je supprime le client partout
        if username in value['chat'] :  # Des chats 
            value['chat'].pop(username)
        if username in value['file'] :  # Des fichiers
            value['file'].pop(username)

    Users.pop(username)  # Enfin, je supprime le client des users

    socket.shutdown(socket.SHUT_RDWR)
    socket.close()
# FIN METHODE

# METHODE MUTE
def mute(socket,username):
    for value in Users.values() :   # prevenir les autres clients   
        code = "120 "+username
        value["port"].sendall(code.encode())
# FIN METHODE

# METHODE UNMUTE
def unmute(socket,username):
    socket.sendall("205".encode())  # message de retour ? pas sur a voir ....

    for value in Users.values() :   # prevenir les autres clients
        code = "121 "+username
        value["port"].sendall(code.encode())  
# FIN METHODE

# METHODE CONNECT username :
def connect(socket,message): 
    
    if not re.match(r"CONNECT [^ ]+$", message):  # On verifie l'orthographe du username
        socket.sendall("402".encode())
        return ""
    elif not re.match(r"CONNECT [a-zA-Z]+", message):
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
            Users[username]['file'] = {}

            for value in Users.values() :   # prevenir les autres clients
                if Users[username]['port'] != value['port'] :
                    code = "119 "+username
                    value["port"].sendall(code.encode())

            return username
            
# FIN METHODE

# METHODE RENAME username:
def rename(socket,message,username):

    if not re.match(r"RENAME [a-zA-Z]+", message) :
            socket.sendall("407".encode())
            return ""
    else :
        y = message.split(" ") # On recupere le username
        new_username=y[1]
        
        if new_username in Users :  # Verification du username
            socket.sendall("406".encode())
            return ""
        else :
            
            for value in Users.values() :
                if username in value['chat'] : # Je modifie le username partout
                    value['chat'][new_username] = value['chat'].pop(username)

            Users[new_username] = Users.pop(username)

            for value in Users.values() :   # prevenir les autres clients
                if Users[new_username]['port'] != value['port'] :
                    code = "203 "+username+" "+new_username #pas trop sur du 203 a voir...
                    value["port"].sendall(code.encode())
            
            socket.sendall("203".encode()) # j'envoie la reponse au client qui vient de se renommer

        return new_username            
# FIN METHODE

# METHODE BROADCAST msg :
def broadcast(socket,message,username):
    y = message.split(" ", 1) # On recupere le username
    broadcast=y[1]

    #socket.sendall("206".encode()) # message de retour a l'envoyeur

    for value in Users.values() :   # prevenir les autres clients
        #if Users[username]['port'] != value['port'] :
            code = "118 "+username+" "+broadcast
            value["port"].sendall(code.encode())

    socket.sendall("206".encode()) # message de retour a l'envoyeur
    #return broadcast            
# FIN METHODE

# METHODE WHISPER user:
def whisper (socket,message,username):
    y = message.split(" ") # On recupere le username avec qui il veut communiquer
    username_chat=y[1]

    if username_chat not in Users or username_chat == username :   # Verification du username : s'il n'existe pas ...
        code= "411 "+username_chat
        socket.sendall(code.encode())

    else :   
        if username_chat in Users[username]['chat'] and Users[username]['chat'][username_chat] == True:
            code= "415 "+username_chat
            socket.sendall(code.encode())
        else :
            for value in Users.values() :   
                if Users[username_chat]['port'] == value['port'] : # Je previens le client concerné qu'on desire chater avec lui 
                    code = "116 "+username
                    value["port"].sendall(code.encode())

            Users[username]['chat'][username_chat] = False  # J'enregistre la demande de tchat chez l'envoyeur

            socket.sendall("101".encode()) # message de retour a l'envoyeur : sa demande a été envoyé      
# FIN METHODE

# METHODE ACCEPTWHISPER user  :
def acceptwhisper (socket,message,username):
    y = message.split(" ")    
    username_chat_sender=y[1]  # On recupere le username avec qui il va se mettre a communiquer
  
    if username_chat_sender not in Users or username_chat_sender == username :   # Verification du username : s'il n'existe pas ...
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
                    
                else : # Il n'a pas encore accepté (chat a False)
                    Users[username_chat_sender]['chat'][username] = True  # Je met le chat a True chez l'envoyeur
                    Users[username]['chat'][username_chat_sender] = True  # Je met le chat a True chez le recepteur (moi)
                    
                    for value in Users.values() :
                        if Users[username_chat_sender]['port'] == value['port'] : # Je previens le client concerné que sa demande de tchat a été acceptée  
                            code_retour = "102 "+username
                            value["port"].sendall(code_retour.encode())
                    
                    code = "106 " + username_chat_sender   # On previent le client qu'il vient d'accepter la demande de whisper
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : il vient d'accepter la demande de whisper   
# FIN METHODE

# METHODE DECLINEWHISPER user  :
def declinewhisper (socket,message,username):
    y = message.split(" ")    # On recupere le username avec qui il va se mettre a communiquer
    username_chat_sender=y[1]

    if username_chat_sender not in Users or username_chat_sender == username :   # Verification du username : s'il n'existe pas ...
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
                    
                else : # Il n'a pas encore accepté (chat a False)
                    Users[username_chat_sender]['chat'].pop(username)
                    
                    for value in Users.values() :

                        if Users[username_chat_sender]['port'] == value['port'] : #  Je previens le client concerné que sa demande de tchat a été refusée 
                            code_retour = "103 "+ username
                            value["port"].sendall(code_retour.encode())

                    
                    code = "107 " + username_chat_sender  # On previent le client qu'il vient de refuser la demande de whisper
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : il vient de reffuser la demande de whisper    
# FIN METHODE


# METHODE WHISPERMESSAGE user msg :
def whispermessage (socket,message,username):
    y = message.split(" ")    
    username_chat_receiver=y[1]  # On recupere le username avec qui il va se mettre a communiquer
    y = message.split(" ",2)
    chat_message=y[2]  # On recupere le message qu'il veut envoyer

    if username_chat_receiver not in Users or username_chat_receiver == username :   # Verification du username : s'il n'existe pas ...
        code= "411 " + username_chat_receiver
        socket.sendall(code.encode())
    
    else :
        if username_chat_receiver not in Users[username]['chat'] :  #  je verifie si le recepteur se trouve dans nos chats
            code = "420 " + username_chat_receiver
            socket.sendall(code.encode())

        else :      #  le recepteur se trouve dans nos demandes de chat  
               # On verifie qu'il a accepté ...
                if Users[username]['chat'][username_chat_receiver] == False : # S'il n'a pas encore accepté
                    code = "420 " + username_chat_receiver
                    socket.sendall(code.encode())  
                    
                elif Users[username]['chat'][username_chat_receiver] == True : # S'il a accepté
                    
                    for value in Users.values() :

                        if Users[username_chat_receiver]['port'] == value['port'] : #  J'envoie le message au client concerné
                            code_retour =  username+" "+chat_message
                            value["port"].sendall(code_retour.encode())
                    
                    code = "108 " + username_chat_receiver  # On previent le client que son message vient d'etre envoye
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : ton message a été envoyé avec succes 
# FIN METHODE

# METHODE ENDWHISPER user:
def endwhisper (socket,message,username):
    y = message.split(" ") 
    username_chat=y[1]   # On recupere le username avec qui il veut arreter de communiquer

    if username_chat not in Users or username_chat == username :   # Verification du username : s'il n'existe pas ...
        code= "411 "+username_chat
        socket.sendall(code.encode())

    else :   # Le username existe

        if username_chat in Users[username]['chat'] :  #  je verifie si le recepteur se trouve dans nos chats

            if Users[username]['chat'][username_chat] == True : # On est en discussion privée avec ce client

                for value in Users.values() :   
                    if Users[username_chat]['port'] == value['port'] : # Je previens le client concerné qu'on a arreté de chater avec lui 
                        code = "122 "+username
                        value["port"].sendall(code.encode())
                
                code = "209 "+username_chat
                socket.sendall(code.encode()) # message de retour a l'envoyeur : son chat est arreté
                
                Users[username_chat]['chat'].pop(username)
                Users[username]['chat'].pop(username_chat)

            else : # On a recu une demande de whisper mais on ne l'a pas encore accepté
                code = "420 "+username_chat
                socket.sendall(code.encode()) # On previent le client qu'il n'est pas en chat privee avec ce username

        else : # On n'a meme pas recu de demande de whisper de ce client
            code = "420 "+username_chat
            socket.sendall(code.encode()) # On previent le client qu'il n'est pas en chat privee avec ce username
# FIN METHODE

# METHODE SENDFILEDEMAND  user:
def sendfiledemand (socket,message,username):
    y = message.split(" ") # On recupere le username a qui il veut envoyer un fichier
    username_file_send = y[1]

    if username_file_send not in Users or username_file_send == username :   # Verification du username : s'il n'existe pas ...
        code= "411 "+username_file_send
        socket.sendall(code.encode())

    else :
        # On verifie si la demande d'envoi de fichier n'est pas deja ouverte
        if username_file_send in Users[username]['file'] and Users[username]['file'][username_file_send] == True:
            code= "416 "+username_file_send
            socket.sendall(code.encode())

        else : 
            for value in Users.values() :   
                if Users[username_file_send]['port'] == value['port'] : # Je previens le client concerné qu'on desire lui envoyer un fichier 
                    code = "117 "+username
                    value["port"].sendall(code.encode())

            Users[username]['file'][username_file_send] = False  # J'enregistre la demande d'envoi de fichier' chez l'envoyeur

            socket.sendall("114".encode()) # message de retour a l'envoyeur : sa demande d'envoi de fichier a été envoyé      
# FIN METHODE

# METHODE ACCEPTSENDFILE user port :
def acceptsendfile (socket,message,username):
    y = message.split(" ")    
    username_file_sender = y[1]  # On recupere le username de qui il va recevoir un fichier
    port_file = y[2]
  
    if username_file_sender not in Users or username_file_sender == username :   # Verification du username : s'il n'existe pas ...
        code= "411 " + username_file_sender
        socket.sendall(code.encode())
    
    else :   #  je verifie si on se trouve ds les demandes de l'envoyeur
        if username not in Users[username_file_sender]['file'] :  #  On ne se trouve pas dans les demandes de l'envoyeur  
            code = "413 " + username_file_sender
            socket.sendall(code.encode())

        else :      #  On se trouve dans les demandes de l'envoyeur  
               # On verifie qu'il n'a pas deja accepté ...
                if Users[username_file_sender]['file'][username] == True : # S'il a deja accepté
                    code = "416 " + username_file_sender
                    socket.sendall(code.encode())
                    
                else : # Il n'a pas encore accepté (file a False)
                    Users[username_file_sender]['file'][username] = True  # Je met la demande de fichier a True chez l'envoyeur
                    
                    for value in Users.values() :

                        if Users[username_file_sender]['port'] == value['port'] : # Je previens le client concerné que sa demande d'envoi de fichier a été acceptée  
                            code_retour = "111 "+username+" "+port_file
                            value["port"].sendall(code_retour.encode())
                    
                    code = "109 " + username_file_sender   # On previent le client qu'il vient d'accepter la demande d'envoi de fichier
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : il vient d'accepter la demande d'envoi de fichier
# FIN METHODE

# METHODE DECLINESENDFILE user port :
def declinesendfile (socket,message,username):
    y = message.split(" ")    
    username_file_sender = y[1]  # On recupere le username de qui il va recevoir un fichier
    port_file = y[2]
  
    if username_file_sender not in Users or username_file_sender == username :   # Verification du username : s'il n'existe pas ...
        code= "411 " + username_file_sender
        socket.sendall(code.encode())
    
    else :
        if username not in Users[username_file_sender]['file'] :  #  je verifie si on se trouve ds les demandes de l'envoyeur
            code = "413 " + username_file_sender
            socket.sendall(code.encode())

        else :      #  On se trouve dans les demandes de l'envoyeur  
               # On verifie qu'il n'a pas deja accepté ...
                if Users[username_file_sender]['file'][username] == True : # S'il a deja accepté
                    code = "416 " + username_file_sender
                    socket.sendall(code.encode())
                    
                else : # Il n'a pas encore accepté (file a False)
                    Users[username_file_sender]['file'].pop(username)
                    
                    for value in Users.values() :

                        if Users[username_file_sender]['port'] == value['port'] : # Je previens le client concerné que sa demande d'envoi de fichier a été refusée  
                            code_retour = "112 "+username
                            value["port"].sendall(code_retour.encode())
                    
                    code = "110 " + username_file_sender  
                    socket.sendall(code.encode()) # message de retour a l'envoyeur : il vient de refuser la demande d'envoi de fichier
# FIN METHODE

# METHODE SENDFILE user path :
def sendfile (socket,message,username):
    y = message.split(" ")    
    username_file_receiver=y[1]  # On recupere le username a qui il va envoyer un fichier
    y = message.split(" ",2)
    file_path=y[2]  # On recupere le chemin du fichier qu'il veut envoyer

    if username_file_receiver not in Users or username_file_receiver == username :   # Verification du username : s'il n'existe pas ...
        code= "411 " + username_file_receiver
        socket.sendall(code.encode())
    
    else :    #  je verifie le recepteur se trouve dans notre liste de demandes
        if username_file_receiver not in Users[username]['file'] :  
            code = "417 " + username_file_receiver
            socket.sendall(code.encode())

        else :   # Le recepteur se trouve dans les demandes de l'envoyeur  
               # On verifie s'il a accepté ...
                if Users[username]['file'][username_file_receiver] == False : # S'il n'a pas encore accepté
                    code = "417 " + username_file_receiver
                    socket.sendall(code.encode())  
                    
                elif Users[username]['file'][username_file_receiver] == True : # S'il a accepté

                    if not os.path.isfile(file_path): # chemin du fichier incorrect
                        socket.sendall("410".encode())   

                    else :  # Chemin du fichier correct
                        for value in Users.values() :
                            if Users[username_file_receiver]['port'] == value['port'] : #  J'envoie le fichier au client concerné
                                code_retour = file_path
                                value["port"].sendall(code_retour.encode())
                        
                        code = "113 " 
                        socket.sendall(code.encode()) # message de retour a l'envoyeur : ton fichier a été envoyé avec succes 

                        Users[username]['file'].pop(username_file_receiver) # Le message est envoye , la discussion fichier est fermée
# FIN METHODE

# METHODE ENDSENDFILE user:
def endsendfile (socket,message,username):
    y = message.split(" ") 
    username_file_receiver=y[1]   # On recupere le username avec qui il veut arreter de communiquer

    if username_file_receiver not in Users or username_file_receiver == username :   # Verification du username : s'il n'existe pas ...
        code= "411 "+username_file_receiver
        socket.sendall(code.encode())

    else :   # Le username existe
        if username_file_receiver in Users[username]['file'] :  #  je verifie si le recepteur se trouve dans la liste

            if Users[username]['file'][username_file_receiver] == True : # On est en discussion fichier avec ce client

                for value in Users.values() :   
                    if Users[username_file_receiver]['port'] == value['port'] : # Je previens le client concerné qu'on a arreté de lui envoyer des fichier 
                        code = "123 "+username
                        value["port"].sendall(code.encode())
                
                code = "210 "+username_file_receiver
                socket.sendall(code.encode()) # message de retour a l'envoyeur : son chat fichier est arreté
                
                Users[username]['file'].pop(username_file_receiver)

            else : # On a envoye une demande d'envoi de fichier mais qui n'a pas encore été acceptée
                code = "417 "+username_file_receiver
                socket.sendall(code.encode()) # On previent le client qu'il n'est pas en chat fichier avec ce username

        else : # On n'a meme pas envoye de demande d'envoi de fichier a ce client
            code = "417 "+username_file_receiver
            socket.sendall(code.encode()) # On previent le client qu'il n'est pas en chat fichier avec ce username
# FIN METHODE


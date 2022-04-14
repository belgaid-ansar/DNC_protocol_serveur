from ast import List
import socket
import threading
import sys
import re
import os.path

Users = {}   # Dictionnaire des utilisateurs

mutex_log = threading.Lock()  # Mutex
mutex_rename = threading.Lock()


# METHODE traiter_client :
def traiter_client(sock_fille, adr_client, logs, username=None):
    CONNECTED = False # varible Connexion
    MUTED = False   # variable Mute

    print("Serveur à l'écoute")

    while True:
        print("Serveur à l'écoute")

        try:
            message = sock_fille.recv(256)
            message = message.decode()
            with mutex_log:
                logs.info("Received " + message + " from " + str(adr_client[0]))

        except:  # Connexion interrompue
            quit(sock_fille, username)
            sock_fille.shutdown(socket.SHUT_RDWR)
            sock_fille.close()
            return

        COMMANDE = match_commande(sock_fille, message)  # je recupere la methode

        if not CONNECTED:
            username = connect(sock_fille, message)
            if username != "":
                username_client = username
                CONNECTED = True

        elif CONNECTED and MUTED :  # S'il s'est mute

            if COMMANDE == "MUTE":
                sock_fille.sendall("414".encode())

            elif COMMANDE == "UNMUTE":
                unmute(sock_fille, username)
                MUTED = False

            elif COMMANDE == "QUIT":
                quit(sock_fille, username)
                MUTED = False

            else:
                sock_fille.sendall("409".encode())

        elif CONNECTED and not MUTED:  # On traite les autres commandes apres la commande CONNECT

            if COMMANDE != "":

                if COMMANDE == "CONNECT":
                    sock_fille.sendall("418".encode())

                elif COMMANDE == "USERS":
                    sock_fille.sendall(("208 " + " ".join(list(Users.keys()))).encode())

                elif COMMANDE == "RENAME":
                    val = rename(sock_fille, message, username_client)
                    if val != "":
                        username_client = val

                elif COMMANDE == "BROADCAST":
                    broadcast(sock_fille, message, username_client)

                elif COMMANDE == "WHISPER":
                    whisper(sock_fille, message, username)

                elif COMMANDE == "ACCEPTWHISPER":
                    acceptwhisper(sock_fille, message, username)

                elif COMMANDE == "DECLINEWHISPER":
                    declinewhisper(sock_fille, message, username)

                elif COMMANDE == "WHISPERMESSAGE":
                    whispermessage(sock_fille, message, username)

                elif COMMANDE == "ENDWHISPER":
                    endwhisper(sock_fille, message, username)

                elif COMMANDE == "SENDFILEDEMAND":
                    sendfiledemand(sock_fille, message, username)

                elif COMMANDE == "ACCEPTSENDFILE":
                    acceptsendfile(sock_fille, message, username, adr_client)

                elif COMMANDE == "DECLINESENDFILE":
                    declinesendfile(sock_fille, message, username)

                elif COMMANDE == "SENDFILE":
                    sendfile(sock_fille, message, username)

                elif COMMANDE == "ENDSENDFILE":
                    endsendfile(sock_fille, message, username)

                elif COMMANDE == "MUTE":
                    mute(sock_fille, username)
                    MUTED = True

                elif COMMANDE == "UNMUTE":
                    sock_fille.sendall("408".encode())

                elif COMMANDE == "QUIT":
                    quit(sock_fille, username)
                    CONNECTED = False

            else:
                sock_fille.sendall("402".encode())
# FIN METHODE

# METHODE match_commande :
def match_commande(socket, commande):
    if re.match(r"CONNECT [^ ]+$", commande):
        return "CONNECT"
    elif re.match(r"USERS", commande):
        return "USERS"
    elif re.match(r"RENAME [^ ]+$", commande):
        return "RENAME"
    elif re.match(r"BROADCAST .+", commande):
        return "BROADCAST"
    elif re.match(r"WHISPER [^ ]+$", commande):
        return "WHISPER"
    elif re.match(r"ACCEPTWHISPER [^ ]+$", commande):
        return "ACCEPTWHISPER"
    elif re.match(r"DECLINEWHISPER [^ ]+$", commande):
        return "DECLINEWHISPER"
    elif re.match(r"WHISPERMESSAGE [^ ]+ .+", commande):
        return "WHISPERMESSAGE"
    elif re.match(r"ENDWHISPER [^ ]+$", commande):
        return "ENDWHISPER"
    elif re.match(r"SENDFILEDEMAND [^ ]+$", commande):
        return "SENDFILEDEMAND"
    elif re.match(r"ACCEPTSENDFILE [^ ]+ [^ ]+$", commande):
        return "ACCEPTSENDFILE"
    elif re.match(r"DECLINESENDFILE [^ ]+$", commande):
        return "DECLINESENDFILE"
    elif re.match(r"SENDFILE [^ ]+ [^ ]+$", commande):
        return "SENDFILE"
    elif re.match(r"ENDSENDFILE [^ ]+$", commande):
        return "ENDSENDFILE"
    elif re.match(r"^MUTE", commande):
        return "MUTE"
    elif re.match(r"^UNMUTE", commande):
        return "UNMUTE"
    elif re.match(r"QUIT", commande):
        return "QUIT"
    else:
        return ""
# FIN METHODE

# METHODE QUIT
def quit(socket, username):
    code = "105 " + username
    Users.pop(username, None)  # Je supprime le client des users

    for value in Users.values():
        # prevenir les autres clients
        value["port"].sendall(code.encode())

        # Je supprime le client partout
        value['chat'].pop(username, None)
        value['file'].pop(username, None)
# FIN METHODE

# METHODE MUTE
def mute(socket, username):
    for value in Users.values():  # prevenir les autres clients
        code = "120 " + username
        value["port"].sendall(code.encode())
# FIN METHODE

# METHODE UNMUTE
def unmute(socket, username):
    for value in Users.values():  # prevenir les autres clients
        code = "121 " + username
        value["port"].sendall(code.encode())
# FIN METHODE


# METHODE CONNECT username :
def connect(socket, message):

    with mutex_rename:

        if not re.match(r"CONNECT [^ ]+$", message):  # On verifie qu'il s'agit bien de la commande CONNECT
            socket.sendall("402".encode())
            return ""
        elif not re.match(r"CONNECT [a-zA-Z]+", message):   # On verifie les caracteres du username
            socket.sendall("407".encode())
            return ""
        else:
            x = message.split(" ")  # On recupere le username
            username = x[1]

            if username in Users:  # Verification du username s'il existe deja ou pas 
                socket.sendall("406".encode())
                return ""
            else:
                print(username, "connected to the server")
                
                Users[username] = {}  # Ajout de l'utilisateur
                Users[username]['port'] = socket
                Users[username]['chat'] = {}
                Users[username]['file'] = {}

                for value in Users.values():  # prevenir les autres clients qu'il vient de se connecter
                    code = "119 " + username
                    value["port"].sendall(code.encode())

                return username # On renvoie le username de connection
# FIN METHODE

# METHODE RENAME username:
def rename(socket, message, username):
    with mutex_rename:

        if not re.match(r"RENAME [a-zA-Z]+", message): # On verife les caracteres du uername
            socket.sendall("407".encode())
            return ""
        else:
            y = message.split(" ")  # On recupere le username
            new_username = y[1]

            if new_username in Users:  # Verification du username
                socket.sendall("406".encode())
                return ""
            
            else:
                for value in Users.values():
                    if username in value['chat']:  # Je modifie le username partout
                        value['chat'][new_username] = value['chat'].pop(username)

                Users[new_username] = Users.pop(username)
                code = "203 " + username + " " + new_username  # pas trop sur du 203 a voir...

                for value in Users.values():  # prevenir les autres clients
                    value["port"].sendall(code.encode())

            print(username, " has been renamed to ",new_username)
            return new_username
    # FIN METHODE

# METHODE BROADCAST msg :
def broadcast(socket, message, username):
    y = message.split(" ", 1)  # On recupere le username
    broadcast = y[1]

    code = "118 " + username + " " + broadcast

    for value in Users.values():  # prevenir les autres clients
        value["port"].sendall(code.encode())
# FIN METHODE

# METHODE WHISPER user:
def whisper(socket, message, username):
    y = message.split(" ")  # On recupere le username avec qui il veut communiquer
    username_chat = y[1]

    if username_chat not in Users or username_chat == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_chat
        socket.sendall(code.encode())

    else:
        if username_chat in Users[username]['chat'] and Users[username]['chat'][username_chat] == True:
            code = "415 " + username_chat
            socket.sendall(code.encode())
        else:
            # Je previens le client concerné qu'on desire chater avec lui 
            code = "116 " + username
            Users[username_chat]['port'].sendall(code.encode())

            Users[username]['chat'][username_chat] = False  # J'enregistre la demande de tchat chez l'envoyeur

            socket.sendall("101".encode())  # message de retour a l'envoyeur : sa demande a été envoyé
# FIN METHODE

# METHODE ACCEPTWHISPER user  :
def acceptwhisper(socket, message, username):
    y = message.split(" ")
    username_chat_sender = y[1]  # On recupere le username avec qui il va se mettre a communiquer

    if username_chat_sender not in Users or username_chat_sender == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_chat_sender
        socket.sendall(code.encode())

    else:
        if username not in Users[username_chat_sender][
            'chat']:  # je verifie si on se trouve ds les demandes de l'envoyeur
            code = "412 " + username_chat_sender
            socket.sendall(code.encode())

        else:  # On se trouve dans les demandes de l'envoyeur
            # On verifie qu'il n'a pas deja accepté ...
            if Users[username_chat_sender]['chat'][username] == True:  # S'il a deja accepté
                code = "415 " + username_chat_sender
                socket.sendall(code.encode())

            else:  # Il n'a pas encore accepté (chat a False)
                Users[username_chat_sender]['chat'][username] = True  # Je met le chat a True chez l'envoyeur
                Users[username]['chat'][username_chat_sender] = True  # Je met le chat a True chez le recepteur (moi)

                code_retour = "102 " + username  # Je previens le client concerné que sa demande de tchat a été acceptée
                Users[username_chat_sender]['port'].sendall(code_retour.encode())

                code = "106 " + username_chat_sender  # On previent le client qu'il vient d'accepter la demande de whisper
                socket.sendall(code.encode())  
# FIN METHODE

# METHODE DECLINEWHISPER user  :
def declinewhisper(socket, message, username):
    y = message.split(" ")  # On recupere le username avec qui il va se mettre a communiquer
    username_chat_sender = y[1]

    if username_chat_sender not in Users or username_chat_sender == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_chat_sender
        socket.sendall(code.encode())

    else:
        if username not in Users[username_chat_sender][
            'chat']:  # je verifie si on se trouve ds les demandes de l'envoyeur
            code = "412 " + username_chat_sender
            socket.sendall(code.encode())

        else:  # On se trouve dans les demandes de l'envoyeur
            # On verifie qu'il n'a pas deja accepté ...
            if Users[username_chat_sender]['chat'][username] == True:  # S'il a deja accepté
                code = "415 " + username_chat_sender
                socket.sendall(code.encode())

            else:  # Il n'a pas encore accepté (chat a False)
                Users[username_chat_sender]['chat'].pop(username)

                code_retour = "103 " + username  # Je previens le client concerné que sa demande de tchat a été refusée
                Users[username_chat_sender]['port'].sendall(code_retour.encode())

                code = "107 " + username_chat_sender  # On previent le client qu'il vient de refuser la demande de whisper
                socket.sendall(code.encode())  
# FIN METHODE


# METHODE WHISPERMESSAGE user msg :
def whispermessage(socket, message, username):
    y = message.split(" ")
    username_chat_receiver = y[1]  # On recupere le username avec qui il va se mettre a communiquer
    y = message.split(" ", 2)
    chat_message = y[2]  # On recupere le message qu'il veut envoyer

    if username_chat_receiver not in Users or username_chat_receiver == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_chat_receiver
        socket.sendall(code.encode())

    else:
        if username_chat_receiver not in Users[username]['chat']:  # je verifie si le recepteur se trouve dans nos chats
            code = "420 " + username_chat_receiver
            socket.sendall(code.encode())

        else:  # le recepteur se trouve dans nos demandes de chat
            # On verifie qu'il a accepté ...
            if Users[username]['chat'][username_chat_receiver] == False:  # S'il n'a pas encore accepté
                code = "420 " + username_chat_receiver
                socket.sendall(code.encode())

            elif Users[username]['chat'][username_chat_receiver] == True:  # S'il a accepté
                code_retour = "115 " + username + " " + chat_message
                Users[username_chat_receiver]['port'].sendall(code_retour.encode())
                socket.sendall(code_retour.encode())
# FIN METHODE

# METHODE ENDWHISPER user:
def endwhisper(socket, message, username):
    y = message.split(" ")
    username_chat = y[1]  # On recupere le username avec qui il veut arreter de communiquer

    if username_chat not in Users or username_chat == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_chat
        socket.sendall(code.encode())

    else:  # Le username existe

        if username_chat in Users[username]['chat']:  # je verifie si le recepteur se trouve dans nos chats

            if Users[username]['chat'][username_chat] == True:  # On est en discussion privée avec ce client

                code = "122 " + username  # Je previens le client concerné qu'on a arreté de chater avec lui
                Users[username_chat]['port'].sendall(code.encode())

                code = "209 " + username_chat
                socket.sendall(code.encode())  # message de retour a l'envoyeur : son chat est arreté

                Users[username_chat]['chat'].pop(username)
                Users[username]['chat'].pop(username_chat)

            else:  # On a recu une demande de whisper mais on ne l'a pas encore accepté
                code = "420 " + username_chat
                socket.sendall(code.encode())  # On previent le client qu'il n'est pas en chat privee avec ce username

        else:  # On n'a meme pas recu de demande de whisper de ce client
            code = "420 " + username_chat
            socket.sendall(code.encode())  # On previent le client qu'il n'est pas en chat privee avec ce username
# FIN METHODE

# METHODE SENDFILEDEMAND  user:
def sendfiledemand(socket, message, username):
    y = message.split(" ")  # On recupere le username a qui il veut envoyer un fichier
    username_file_send = y[1]

    if username_file_send not in Users or username_file_send == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_file_send
        socket.sendall(code.encode())

    else:
        # On verifie si la demande d'envoi de fichier n'est pas deja ouverte
        if username_file_send in Users[username]['file'] and Users[username]['file'][username_file_send] == True:
            code = "416 " + username_file_send
            socket.sendall(code.encode())

        else:
            code = "117 " + username  # Je previens le client concerné qu'on desire lui envoyer un fichier
            Users[username_file_send]['port'].sendall(code.encode())

            Users[username]['file'][username_file_send] = False  # J'enregistre la demande d'envoi de fichier' chez l'envoyeur

            socket.sendall("114".encode())  # message de retour a l'envoyeur : sa demande d'envoi de fichier a été envoyé
# FIN METHODE

# METHODE ACCEPTSENDFILE user port :
def acceptsendfile(socket, message, username, adr_client):
    y = message.split(" ")
    username_file_sender = y[1]  # On recupere le username de qui il va recevoir un fichier
    port_file = y[2]

    if username_file_sender not in Users or username_file_sender == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_file_sender
        socket.sendall(code.encode())

    else:  # je verifie si on se trouve ds les demandes de l'envoyeur
        if username not in Users[username_file_sender]['file']:  # On ne se trouve pas dans les demandes de l'envoyeur
            code = "413 " + username_file_sender
            socket.sendall(code.encode())

        else:  # On se trouve dans les demandes de l'envoyeur
            # On verifie qu'il n'a pas deja accepté ...
            if Users[username_file_sender]['file'][username] == True:  # S'il a deja accepté
                code = "416 " + username_file_sender
                socket.sendall(code.encode())

            else:  # Il n'a pas encore accepté (file a False)
                Users[username_file_sender]['file'][username] = True  # Je met la demande de fichier a True chez l'envoyeur

                code_retour = "111 " + username + " " + adr_client[0] + " " + port_file  # Je previens le client concerné que sa demande d'envoi de fichier a été acceptée
                Users[username_file_sender]['port'].sendall(code_retour.encode())

                code = "109 " + username_file_sender  # On previent le client qu'il vient d'accepter la demande d'envoi de fichier
                socket.sendall(code.encode())
# FIN METHODE

# METHODE DECLINESENDFILE user port :
def declinesendfile(socket, message, username):
    y = message.split(" ")
    username_file_sender = y[1]  # On recupere le username de qui il va recevoir un fichier

    if username_file_sender not in Users or username_file_sender == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_file_sender
        socket.sendall(code.encode())

    else:
        if username not in Users[username_file_sender][
            'file']:  # je verifie si on se trouve ds les demandes de l'envoyeur
            code = "413 " + username_file_sender
            socket.sendall(code.encode())

        else :  # On se trouve dans les demandes de l'envoyeur
            # On verifie qu'il n'a pas deja accepté ...
            if Users[username_file_sender]['file'][username] == True:  # S'il a deja accepté
                code = "416 " + username_file_sender
                socket.sendall(code.encode())

            else :  # Il n'a pas encore accepté (file a False)
                Users[username_file_sender]['file'].pop(username)

                code_retour = "112 " + username  # Je previens le client concerné que sa demande d'envoi de fichier a été refusée
                Users[username_file_sender]['port'].sendall(code_retour.encode())

                code = "110 " + username_file_sender  # message de retour a l'envoyeur : il vient de refuser la demande d'envoi de fichier
                socket.sendall(code.encode())
# FIN METHODE


# METHODE SENDFILE user path :
def sendfile(socket, message, username):
    y = message.split(" ")
    username_file_receiver = y[1]  # On recupere le username a qui il va envoyer un fichier
    y = message.split(" ", 2)
    file_path = y[2]  # On recupere le chemin du fichier qu'il veut envoyer

    if username_file_receiver not in Users or username_file_receiver == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_file_receiver
        socket.sendall(code.encode())

    else:  # je verifie le recepteur se trouve dans notre liste de demandes
        if username_file_receiver not in Users[username]['file']:
            code = "417 " + username_file_receiver
            socket.sendall(code.encode())

        else:  # Le recepteur se trouve dans les demandes de l'envoyeur
            # On verifie s'il a accepté ...
            if Users[username]['file'][username_file_receiver] == False:  # S'il n'a pas encore accepté
                code = "417 " + username_file_receiver
                socket.sendall(code.encode())

            elif Users[username]['file'][username_file_receiver] == True:  # S'il a accepté
                code_retour = "124 "  # J'envoie le code au client concerné
                Users[username_file_receiver]['port'].sendall(code_retour.encode())

                code = "113 "
                socket.sendall(code.encode())  # message de retour a l'envoyeur : ton fichier a été envoyé avec succes

                Users[username]['file'].pop(username_file_receiver)  # Le message est envoye , la discussion fichier est fermée
# FIN METHODE

# METHODE ENDSENDFILE user:
def endsendfile(socket, message, username):
    y = message.split(" ")
    username_file_receiver = y[1]  # On recupere le username avec qui il veut arreter de communiquer

    if username_file_receiver not in Users or username_file_receiver == username:  # Verification du username : s'il n'existe pas ...
        code = "411 " + username_file_receiver
        socket.sendall(code.encode())

    else:  # Le username existe
        if username_file_receiver in Users[username]['file']:  # je verifie si le recepteur se trouve dans la liste

            if Users[username]['file'][username_file_receiver] == True:  # On est en discussion fichier avec ce client

                code = "123 " + username  # Je previens le client concerné qu'on a arreté de lui envoyer des fichier
                Users[username_file_receiver]['port'].sendall(code.encode())

                code = "210 " + username_file_receiver
                socket.sendall(code.encode())  # message de retour a l'envoyeur : son chat fichier est arreté

                Users[username]['file'].pop(username_file_receiver)

            else:  # On a envoye une demande d'envoi de fichier mais qui n'a pas encore été acceptée
                code = "417 " + username_file_receiver
                socket.sendall(code.encode())  # On previent le client qu'il n'est pas en chat fichier avec ce username

        else:  # On n'a meme pas envoye de demande d'envoi de fichier a ce client
            code = "417 " + username_file_receiver
            socket.sendall(code.encode())  # On previent le client qu'il n'est pas en chat fichier avec ce username
# FIN METHODE

import configparser
import logging

from methodes import *


config = configparser.ConfigParser()
config.read('dncserver.conf')
port = int(config['parametres']['port_serveur'])
log_file = config['parametres']['fichier_log']

sock_locale = socket.socket()
ip = socket.gethostbyname(socket.gethostname())
sock_locale.bind((ip, port))
sock_locale.listen(4)

print("Serveur en attente sur le port " + str(port), file=sys.stderr)
logging.basicConfig(filename=log_file, filemode="w", format='%(asctime)s: %(message)s'
                    , datefmt="%Y/%m/%d %H:%M:%S", level=logging.INFO)
logging.info("Server started")
logging.info("Listen on :" + str(port))


while True:
    try:
        sock_client, adr_client = sock_locale.accept()
        threading.Thread(target=traiter_client, args=(sock_client, adr_client, logging)).start()
    except KeyboardInterrupt:
        break

sys.exit(0)


from methodes import *
 
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

'''sock_locale.shutdown(socket.SHUT_RDWR)
print("Bye")

for t in threading.enumerate():
    if t != threading.main_thread(): 
        t.join
        print("Arret du serveur", file=sys.stderr)'''

sys.exit(0)

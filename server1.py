import socket
import select

HEADER_LENGTH=10
IP = "127.0.0.1"
PORT = 6933

#AF_INET is for ip address and SOCK_STREAM is TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#binding the sever with an ip and port address in this case we took IPV4
#Warnig!!! be careful with the port because you don't want to step into some other apps running on other ports
server_socket.bind((IP, PORT))

#listen function actually gets your messages
server_socket.listen()

#socket list holds the data about all the people sharing the group
sockets_list = [server_socket]

#clients is a dictionary with the user and address pairs
clients={}



def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        message_length=int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    #Exception is hit only if client closes harshly
    except:
        return False



while True:
    read_sockets, _, exception_sockets = select.select(sockets_list,[],sockets_list)
    for notified_socket in read_sockets:
        if notified_socket== server_socket:
            #accepting the requests
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            #appending the users list
            clients[client_socket]=user
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username{user['data'].decode('utf-8')}")
        else:
            message = receive_message(notified_socket)
            if message is False:
                print("Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data']+message['header']+message['data'])
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_sockets)
        del clients[notified_socket]

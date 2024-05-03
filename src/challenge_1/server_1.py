import socket
import select
import sys
import threading
import re

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ip_address = '127.0.0.1'
port = 8081

server.bind((ip_address, port))
server.listen(100)

list_of_clients = []

def clientthread(conn, addr):
    while True:
        try:
            message = conn.recv(2048).decode()
            if message:
                if re.match(r'^[0-9\+\-\*\/\s]+$', message):
                    result = eval(message)
                    message_to_send = f"{message} = {result}"
                    print('<' + addr[0] + '>' + ' ' + message_to_send)
                    conn.send(message_to_send.encode())
                else:
                    print('<' + addr[0] + '>' + ' ' + message)
                    broadcast('<' + addr[0] + '>' + ' ' + message, conn)
            else:
                remove(conn)
        except Exception as e:
            print("Error:", e)
            remove(conn)
            break

def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message.encode())
            except:
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print('\n' + addr[0] + ' ~ connected')
    threading.Thread(target=clientthread, args=(conn, addr)).start()

conn.close()

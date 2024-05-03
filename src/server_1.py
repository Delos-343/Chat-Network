import socket
import select
import sys
import threading
import re
from fractions import Fraction
from ast import literal_eval

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ip_address = '127.0.0.1'
port = 8081

server.bind((ip_address, port))
server.listen(100)

list_of_clients = []

def evaluate_expression(expression):
    try:
        # Using literal_eval to safely evaluate the expression
        result = literal_eval(expression)
        return result
    except Exception as e:
        print("Error evaluating expression:", e)
        return None

def clientthread(conn, addr):
    while True:
        try:
            message = conn.recv(2048).decode()
            if message:
                # Check if the message is a mathematical expression
                if re.match(r'^[\d\s\+\-\*\/\(\)]+$', message):
                    result = evaluate_expression(message)
                    if result is not None:
                        # Send the result to all clients
                        message_to_send = f'{message} = {result}\n'
                        broadcast(message_to_send, conn)
                else:
                    print('<' + addr[0] + '>' + message)
                    message_to_send = '<' + addr[0] + '>' + message
                    broadcast(message_to_send, conn)
            else:
                remove(conn)
        except Exception as e:
            print("Error handling client message:", e)
            continue

def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message.encode())
            except Exception as e:
                print("Error broadcasting message:", e)
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

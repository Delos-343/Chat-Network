import socket
import select
import sys
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ip_address = '127.0.0.1'
port = 8081

server.bind((ip_address, port))
server.listen(100)

list_of_clients = {}
client_id_counter = 1

def clientthread(conn, addr):
    global client_id_counter
    conn.send(f"\n\nWelcome to the chat!\n\nYour ID is {client_id_counter}\n\n".encode())
    client_id = client_id_counter
    list_of_clients[client_id] = conn
    client_id_counter += 1

    print(f'\n<{addr[0]}> Client {client_id} ~ connected')  # Log client connection with address and ID

    while True:
        try:
            message = conn.recv(2048).decode()
            if message:
                if message.lower() == "list":
                    send_client_list(conn)
                elif message.startswith("private"):
                    handle_private_message(message, client_id)
                else:
                    broadcast(f'<Client {client_id}> {message}', conn)
            else:
                remove(conn)
        except Exception as e:
            print(e)
            continue

def send_client_list(conn):
    conn.send("List of participants:\n".encode())
    for client_id in list_of_clients:
        if client_id != conn:
            conn.send(f"Client {client_id}\n".encode())

def handle_private_message(message, sender_id):
    parts = message.split(maxsplit=2)
    if len(parts) == 3:
        dest_id = int(parts[1])
        dest_conn = list_of_clients.get(dest_id)
        if dest_conn:
            dest_conn.send(f'<Private from {sender_id}> {parts[2]}'.encode())
        else:
            list_of_clients[sender_id].send(f"Client {dest_id} is not connected.\n".encode())
    else:
        list_of_clients[sender_id].send("Invalid private message syntax.\n".encode())

def broadcast(message, connection):
    for client_id, client_conn in list_of_clients.items():
        if client_conn != connection:
            try:
                client_conn.send(message.encode())
            except:
                client_conn.close()
                remove(client_conn)

def remove(connection):
    for client_id, client_conn in list_of_clients.items():
        if client_conn == connection:
            del list_of_clients[client_id]
            print(f'<{client_conn.getpeername()[0]}> Client {client_id} disconnected')  # Log client disconnection with address and ID
            break

while True:
    conn, addr = server.accept()
    threading.Thread(target=clientthread, args=(conn, addr)).start()

conn.close()

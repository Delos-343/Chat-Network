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

list_of_clients = []

def clientthread(conn, addr):
  while True:
    try:
      message = conn.recv(2048).decode()
      if message:
        if message:
          print('<' + addr[0] + '>' + message)
          message_to_send = '<' + addr[0] + '>' + message
          broadcast(message_to_send, conn)
      else:
        remove(conn)
    except:
      continue

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

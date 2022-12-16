#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 12345))
messages = []

def receive():
    while True:
        message = client.recv(1024).decode('ascii')
        if message == 'NAME':
            client.send(input("Enter your name: ").encode('ascii'))

        elif message == 'TOO MANY':
            print("There are too many players or game is running, try later.")
            client.close()
            break

        elif message == 'ZERO':
            client.send("REMOVED_RECV".encode('ascii'))

        elif message == 'REPEAT':
            client.send(messages[-1].encode('ascii'))

        elif message == 'QUIT':
            print("Leaving...")
            client.close()
            break

        else:
            print(message)

def write():
    while True:
        message = input()
        client.send(message.encode('ascii'))
        messages.append(message)

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()


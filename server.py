#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import threading
import random
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen()
print("Socket created, waiting for connections...")

clients = []
names = []
score = []
answer_saved = False
number_of_question = 0
game_on = False

def broadcast(message):
    for client in clients:
        client.send(message.encode('ascii'))

def handle(client):
    while True:
        message = client.recv(1024).decode('ascii')
        index = clients.index(client)
        global game_on

        if message == 'START' and index == 0 and (2 <= len(clients) <= 4):
            broadcast("Player 1 started a game, it will begin in 5 seconds!\nType only 'YES' or 'NO', otherwise you will recieve 0 points\nYou have 5 seconds for every question, otherwise it will be skipped!\nIf somebody answer correctly in that time, question will also be skipped\nGood luck!")
            time.sleep(5)
            for i in range(len(clients)):
                score.append([])

            game(clients)

        elif message == 'START' and index == 0 and len(clients) < 2:
            client.send("Not enought players".encode('ascii'))

        elif game_on == False and index != 0 and message == 'START':
            client.send("Only 1 player can start game".encode('ascii'))

        elif game_on == True and index != 0 and (message == 'YES' or message == 'NO'):
            client.send("REPEAT".encode('ascii'))

        elif game_on == True and index != 0 and (message != 'YES' or message != 'NO'):
            client.send("".encode('ascii'))

        elif game_on == False and message == 'QUIT':
            client.send('QUIT'.encode('ascii'))
            clients.remove(client)
            nickname = names[index]
            names.remove(nickname)
            broadcast("{} left server".format(nickname))

        else:
            client.send("Server didn't understand the message".encode('ascii'))

def receive():
    while True:
        if len(clients) < 4 and len(score) == 0:
            client, address = server.accept()
            client.send('NAME'.encode('ascii'))
            name = client.recv(1024).decode('ascii')
            names.append(name)
            clients.append(client)

            print("{} joined server, he is player number {}, his address: {}, ".format(name, len(clients),address))
            client.send("Welcome to the server!\nType 'START' to start game (only 1 player is able to run it).\nType 'QUIT' to exit server while game is off".encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        else:
            client, address = server.accept()
            client.send('TOO MANY'.encode('ascii'))


def game(clients):
    global answer_saved
    global number_of_question
    global game_on
    game_on = True
    questions = {"2 + 2 = 4" : "YES",
                "5 - 10 = -6": "NO",
                "180 - 179 = 1" : "YES",
                "4 * 2 = 7" : "NO",
                "10 / 2 = 5": "YES",
                "69 + 14 = 154" : "NO",
                "2 + 22 = 24" : "YES",
                "5! = 121": "NO",
                "5! = 120" : "YES",
                "560 / 10 = 55" : "NO",
                "45 + 13 = 58": "YES",
                "654 - 123 = 532" : "NO",
                "5 + 7 = 12" : "YES",
                "5 - 8 = -2": "NO",
                "5 * 6 = 30" : "YES",
                "5 * 4 = 15" : "NO",
                "65 / 5 = 13": "YES",
                "12 - 12 = 1" : "NO",
                "13 + 87 = 100" : "YES",
                "100 / 4 = 20": "NO"
            }
    numbers = list(range(0,20))
    for i in range(10):
        answer_saved = False
        number_of_question = i + 1
        number = random.choice(numbers)
        numbers.remove(number)
        key = list(questions)[number]
        value = list(questions.values())[number]

        broadcast(key)

        for client in clients:
            thread_answer = threading.Thread(target=get_answer, args=(client, value))
            thread_answer.start()

        time_end = time.time() + 5 * 1
        while time.time() < time_end:
            if answer_saved == True:
                break
            else:
                continue

        for client in clients:
            index_for_zero = clients.index(client)
            if len(score[index_for_zero]) != number_of_question:
                if index_for_zero != 0:
                    client.send("ZERO".encode('ascii'))
                    client.send("ZERO".encode('ascii'))
                else:
                    client.send("ZERO".encode('ascii'))
                score[index_for_zero].append(0)
            else:
                pass

        print(*score)

    print("Game finished succesfully")
    broadcast("Game finished succesfully, final score:")
    final_score = find_results(score)
    for i in final_score:
        broadcast(i)

    score.clear()
    game_on = False

def get_answer(client, value):
    global answer_saved
    global number_of_question
    index = clients.index(client)

    if check_three_answers(index) == True:
        client.send("You answered incorrectly 3 times in a row, you recieve 0 points for that question".encode("ascii"))
        score[index].append(0)
    else:
        answer = client.recv(1024).decode('ascii')
        if answer == value:
            score[index].append(1)
            answer_saved = True
            client.send('GOOD'.encode('ascii'))
        elif answer == "REMOVED_RECV":
            pass
        elif answer != "YES" and answer != "NO" and index == 0:
            score[index].append(0)
        else:
            score[index].append(-2)
            client.send("WRONG".encode('ascii'))

def check_three_answers(index):
    if sum(score[index][-3:]) == -6:
        return True
    else:
        return False

def find_results(score):
    points = []
    for i in score:
        points.append(sum(i))

    table = []
    zipped = zip(names, points)
    for name, point in zipped:
        table.append("{} has got {} points\n".format(name, point))
    return table

receive()


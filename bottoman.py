"""
04-10-2018

author: cassidoxa
"""

import socket

import config

class TwitchBot:

    def __init__(self):

        self.s = self.open_socket()

        self.active_game = False
        self.read_buffer = ""

    def open_socket(self):

        self.s = socket.socket()
        self.s.connect((config.HOST, config.PORT))
        self.s.send(f'PASS {config.token} \r\n'.encode('utf-8'))
        self.s.send(f'NICK {config.bot_name} \r\n'.encode('utf-8'))
        self.s.send(f'JOIN {config.bot_channel} \r\n'.encode('utf-8'))
        return self.s

    def join_room(self, s):

        readbuffer = ""
        loading = False
        while not loading:
            readbuffer = readbuffer + self.s.recv(2048).decode()
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:
                print(line)
                loading = self.loading_complete(line)

    def loading_complete(self, line):
        return "End of /NAMES list" in line

    def get_user(self, line):
        """
        Extract the user from a response
        """
        separate = line.split(":", 2)
        user = separate[1].split("!", 1)[0]
        return user.rstrip()

    def get_message(self, line):
        """
        Extract the message from a response
        """
        separate = line.split(":", 2)
        message = separate[2]
        return message.rstrip()

    def send_message(self, message):
        """
        Send a message to chat
        """
        messageTemp = f'PRIVMSG #{config.bot_channel} :{message}'
        self.s.send(f'{messageTemp}\r\n'.encode('utf-8'))
        print(f'Sent: {messageTemp}')

    def whisper(self, user, message):
        """
        Whisper to a user, i.e. Private message
        """
        self.send_message('/w ' + user + ' ' + message)
        print("Whispered to " + user + ': ' + message)

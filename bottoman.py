"""
04-10-2018

author: cassidoxa
"""

import socket
import json

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

        read_buffer = ""
        loading = False
        while not loading:
            read_buffer = read_buffer + self.s.recv(2048).decode()
            temp = read_buffer.split("\n")
            read_buffer = temp.pop()

            for line in temp:
                print(line)
                if "End of /NAMES list" in line:
                    loading = True

    def get_user(self, line):
        """
        Extract the user from a response
        """
        separate = line.split(":", 2)
        user = separate[1].split("!", 1)[0]
        print(user) #        
        return user.rstrip()

    def get_message(self, line):
        """
        Extract the message from a response
        """
        separate = line.split(":", 2)
        message = separate[2]

        if message[0] == '!':
            run_command(message)        
        else:
            pass
        print (message) #
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

    #functions for running chat commands in the format !example, loaded from command.json in run.py initialization
    
    @staticmethod
    def load_commands(command_file):
        with open(command_file, 'r') as f:
            command_list = json.load(f)
        return command_list

    def run_command(message, command_dict):
        command = message.split()[0][1:]
        print(command_dict[command])

    def runtime(self):
        while True:
            read_buffer = self.read_buffer + self.s.recv(2048).decode()
            temp = read_buffer.split("\n")
            read_buffer = temp.pop()

            for line in temp:

                if (line.startswith("PING ")):    # If PING, respond with PONG
                    self.s.send(b"PONG http://localhost\r\n")
                    break

                user = self.get_user(line)
                message = self.get_message(line)
                # Should probably do logging rather than just printing to console
                print(user + " typed: " + message)

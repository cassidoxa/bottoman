"""
04-10-2018

author: cassidoxa
"""

import socket
import json
import re

import config

class TwitchBot:

    def __init__(self):

        self.s = self.open_socket()

        self.active_game = False
        self.read_buffer = ""
        self.command_dict = self.load_commands('commands.json')

    #functions for initializing bot, joining room, loading static commands   

    def open_socket(self):

        self.s = socket.socket()
        self.s.connect((config.HOST, config.PORT))
        self.s.send(f'PASS {config.token} \r\n'.encode('utf-8'))
        self.s.send(f'NICK {config.bot_name} \r\n'.encode('utf-8'))
        self.s.send(f'JOIN #{config.bot_channel} \r\n'.encode('utf-8'))
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
    
    def load_commands(self, command_file):
        with open(command_file, 'r') as f:
            command_list = json.load(f)
        return command_list

    #functions for parsing messages, running commands, and sending messages from the bot

    def parse_message(self, line):
        
        #parse message into list for further processing, respond to server pings
        #return user and clean message
        separate = re.split('[:!]', line, 3)
        if separate[0].rstrip() == 'PING':  
            self.s.send(b"PONG http://localhost\r\n")
            print('PONG')
        else:
            user = separate[1]
            message = separate[3].rstrip()
            return (user, message)

    def handle_message(self, user, message):
        
        print(f'{user} wrote: {message}') #
        if message[0] == '!':
            command = message[1:]
            if command in self.command_dict:
                self.send_message(self.command_dict[command])
            elif command not in self.command_dict:
                pass
        else:
            pass

    def send_message(self, message):

        messageTemp = f'PRIVMSG #{config.bot_channel} :{message}'
        self.s.send(f'{messageTemp}\r\n'.encode('utf-8'))
        print(f'Sent: {messageTemp}')

    def whisper(self, user, message):

        self.send_message('/w ' + user + ' ' + message)
        print("Whispered to " + user + ': ' + message)

    #main infinite loop

    def run_time(self):
        while True:
            read_buffer = self.read_buffer + self.s.recv(2048).decode()
            user, message = self.parse_message(read_buffer)

            self.handle_message(user, message)

#            for line in temp:
#                user = self.get_user(line)
#                message = self.parse_message(line)
#                
#                self.handle_message(message)
#                print(f'{user} typed: {message}')


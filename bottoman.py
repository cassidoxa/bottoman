"""
04-10-2018

author: cassidoxa
"""

import socket
import json
import select

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

    def get_user(self, line):

        separate = line.split(":", 2)
        user = separate[1].split("!", 1)[0]        
        return user.rstrip()

    def parse_message(self, line):
        
        #handle pings from server first
        if (line.startswith("PING ")):  
            self.s.send(b"PONG http://localhost\r\n")
            print('PONG')
        
        else:
            separate = line.split(":", 2)
            message = separate[2] 
            return message.rstrip()

    def handle_message(self, message):
        
        if message[0] == '!':
            command = message[1:]
            self.run_command(command)
        else:
            pass

    def run_command(self, message):
        command = message
        self.send_message(self.command_dict[command])

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
            temp = read_buffer.split("\n")
            read_buffer = temp.pop()

            for line in temp:
                user = self.get_user(line)
                message = self.parse_message(line)
                
                self.handle_message(message)
                print(f'{user} typed: {message}')


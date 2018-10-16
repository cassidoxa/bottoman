"""
04-10-2018

author: cassidoxa
"""

import socket
import json
import re
import time

import config
from chatters import ChattersHandler

class TwitchBot:

    def __init__(self):

        self.s = self.open_socket()

        self.active_game = False
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
        
        #first check if None
        #parse message into list for further processing, respond to server pings
        #return user, clean message, and unix time(for points timeout)

        separate = re.split('[:!]', line, 3)
        if separate[0].rstrip() == 'PING':  
            self.s.send(b"PONG http://localhost\r\n")
            comment_time = int(time.time())
            return ("twitch_server", "ping", comment_time)
        else:
            user = separate[1]
            message = separate[3].rstrip()
            comment_time = int(time.time())
            return (user, message, comment_time)

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
           
            read_buffer = self.s.recv(2048).decode()
            user, message, comment_time = self.parse_message(read_buffer)

            print(f'{user} wrote: {message} at {comment_time}')



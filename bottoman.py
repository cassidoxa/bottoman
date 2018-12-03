import socket
import json
import re
import time

import config
import messagehandler

class TwitchBot:

    def __init__(self):

        self.s = self.open_socket()
        self.reminder_counter = [0, time.time()]
        self.active_game = False
        self.points_toggle = True
        
    #functions for initializing bot, joining room  

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


    #functions for parsing messages, running commands, and sending messages from the bot

    def send_message(self, message):

        messageTemp = f'PRIVMSG #{config.bot_channel} :{message}'
        self.s.send(f'{messageTemp}\r\n'.encode('utf-8'))
        print(f'Sent: {messageTemp}')

    def parse_message(self, line):
        """
        takes chat data from twitch and returns a clean user, message, and unix time to give to message handler
        """
        
        separate = re.split('[:!]', line, 3)
        if separate[0].rstrip() == 'PING':  
            self.s.send(b"PONG http://localhost\r\n")
            return ("twitch server", "ping", 0)
        else:
            user = separate[1]
            message = separate[3].rstrip()
            comment_time = int(time.time())
            return (user, message, comment_time)

    def reminder_message(self):
        """
        send a message to chat at a regular interval based on time or number of messages
        also checks to see if these values are set to 0 in config.py and dis
        """
        
        post_number = self.reminder_counter[0]
        reminder_timer = self.reminder_counter[1]
        if (post_number >= config.reminder_posts and config.reminder_posts != 0) or ((time.time() - reminder_timer > config.reminder_seconds) and config.reminder_seconds != 0):
            with open('commands.json', 'r') as f:
                commands_dict = json.load(f)
            if commands_dict["chat reminder"] == "none":
                self.reminder_counter = [0, time.time()]
                return
            else:
                self.send_message(commands_dict["chat reminder"])
                self.reminder_counter = [0, time.time()]
        return

    def instruction_handler(self, instructions):
        if "increment" in instructions:
            self.reminder_counter[0] += 1
        
        if "ptoggle on" in instructions:
            self.points_toggle = True

        if "ptoggle off" in instructions:
            self.points_toggle = False

        return

    #main infinite loop

    def run_time(self):
        """
        recieves data from twitch, parses it, gives individual messages to message handler for further processing
        the message handler can return an instruction to the bot in the "instruction" variable.
        checks if there is an active game and handles messages differently while game is running until game stops
        """

        while True:
            read_buffer = self.s.recv(2048).decode()
            user, message, comment_time = self.parse_message(read_buffer)

            if self.active_game == False:
                message_handler = messagehandler.MessageHandler(user, message, comment_time, self.s, self.active_game, self.points_toggle)
                instruction = message_handler.handle_message()
                print(instruction) #
            
            elif self.active_game == True:
                pass

            self.instruction_handler(instruction)
            self.reminder_message()




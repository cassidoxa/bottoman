import random
import re
import socket
import sqlite3
import sys
import time

import config
from db.db import DatabaseManager
#import games.game
import messagehandler as mh

class TwitchBot:

    def __init__(self):

        init_time = time.time()
        self.s = self.open_socket()
        self.reminder_counter = [0, init_time]
        self.active_game = None
        self.points_toggle = True
        self.dbmgr = DatabaseManager('db/bottoman.db')
        self.append_timer = init_time
        self.append_cooldown = self.dbmgr.query("SELECT config_number FROM config WHERE config_option=?", ('append_cooldown',)).fetchone()[0]

    #functions for initializing bot, joining room

    def open_socket(self):

        self.s = socket.socket()
        self.s.connect(('irc.twitch.tv', 6667))
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

    def whisper(self, user, message):

        self.send_message(f'/w {user} {message}')
        print(f'Whispered to {user} : {message}')

    def parse_message(self, line):
        """
        takes chat data from twitch and returns a user, message, and unix time to give to message handler
        the PING-PONG call and response is also handled in this function for convenience
        """

        separate = re.split('[:!]', line, 3)
        if separate[0].rstrip() == 'PING':
            self.s.send(b"PONG http://localhost\r\n")
            return ("twitch server", "ping", 0)
        else:
            user = separate[1]
            message = separate[3].rstrip()
            message_time = int(time.time())
            return (user, message, message_time)

    def reminder_message(self):
        """
        send a message to chat at a regular interval based on time or number of messages
        also checks to see if these values are set to 0 in db, disables if 0
        """

        post_number = self.reminder_counter[0]
        reminder_timer = self.reminder_counter[1]
	
        reminder_messages = self.dbmgr.query("SELECT config_number FROM config WHERE config_option=?", ('reminder_interval_messages',)).fetchone()[0]
        reminder_seconds = self.dbmgr.query("SELECT config_number FROM config WHERE config_option=?", ('reminder_interval_seconds',)).fetchone()[0]

        if (post_number >= reminder_messages and reminder_messages != 0) or ((time.time() - reminder_timer > reminder_seconds) and reminder_seconds != 0):
            reminder_msg = self.dbmgr.query("SELECT config_text FROM config WHERE config_option=?", ('reminder_message',)).fetchone()[0]
            if reminder_msg == "none":
                self.reminder_counter = [0, time.time()]
                return
            else:
                self.send_message(reminder_msg)
                self.reminder_counter = [0, time.time()]
        return

    def instruction_handler(self, instructions):

        if 'increment' in instructions[0]:
            self.reminder_counter[0] += 1

        if 'ptoggle on' in instructions[0]:
            self.points_toggle = True

        if 'ptoggle off' in instructions[0]:
            self.points_toggle = False

        if instructions[1]['sendmsg'] != None:
            self.send_message(instructions[1]['sendmsg']) 

        if instructions[1]['sendwhisper'] != None:
            self.whisper(instructions[1]['sendwhisper'][0], instructions[1]['sendwhisper'][1])

        if instructions[1]['appendcooldown'] != None:
            self.append_cooldown = instructions[1]['appendcooldown']

        #if instructions[1]['game_instruction'] == 'start':
        #    game.Game(instructions[1]['game_name'])

        if 'shutdown' in instructions[0]:
            self.send_message(f'{config.exit_msg}')
            sys.exit()

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
            msg_info = self.parse_message(read_buffer)

            self.reminder_message()

            if msg_info[0] == 'twitch server':
                continue

            message_handler = mh.MessageHandler(msg_info, self.active_game, self.points_toggle, self.dbmgr)
            message_handler.handle_message()

            if not self.active_game:

                if msg_info[2] - self.append_timer >= self.append_cooldown and self.append_cooldown != 0 and msg_info[1][0] != '!':
                   self.append_to(msg_info[1])

            elif self.active_game:

                active_game.take_chatter_input(msg_info)

                pass

            self.instruction_handler(message_handler.bot_instructions)

#additional functions

#message appending

    def append_to(self, message):
        """
        appends message with strings added via user commands
        checks whether user wants a new sentence or not and formats appropriately
        returns message for bot to send to chat
        """

        append_strings = [a_str[0] for a_str in self.dbmgr.query("SELECT append_string FROM append_strings")]

        if not append_strings:
            return

        a_string = random.choice(append_strings)

        is_sentence = a_string[0].isupper()
        is_terminated = (message[-1] in ['.', '!', '?'])

        if is_sentence == True:
            if is_terminated == True:
                new_message = ' '.join([message, a_string])
                self.send_message(new_message)
            elif is_terminated == False:
                new_message = '. '.join([message, a_string])
                self.send_message(new_message)

        if is_sentence ==False:
            if is_terminated == True:
                new_message = ' '.join([message[:-1], a_string])
                self.send_message(new_message)
            elif is_terminated == False:
                new_message = ' '.join([message, a_string])
                self.send_message(new_message)

        self.append_timer = time.time()

        return

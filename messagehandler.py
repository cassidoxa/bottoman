import json
import time
import config

from config import points_cooldown, message_points

class MessageHandler:

    def __init__(self, user, message, comment_time, s):
        
        self.user = user
        self.message = message
        self.comment_time = comment_time
        self.s = s
        
        self.chatters_dict = self.load_chatters('chatters.json')
        self.commands_dict = self.load_commands('commands.json')

    def send_message(self, message):

        messageTemp = f'PRIVMSG #{config.bot_channel} :{message}'
        self.s.send(f'{messageTemp}\r\n'.encode('utf-8'))
        print(f'Sent: {messageTemp}')

    #functions for loading and saving persistent data

    def load_chatters(self, chatters_file):
        
        with open(chatters_file, 'r') as f:
            chatters = json.load(f)
        return chatters

    def load_commands(self, command_file):
        with open(command_file, 'r') as f:
            command_list = json.load(f)
        return command_list

    def write_chatters(self):
        
        with open('chatters.json', 'w') as f:
            json.dump(self.chatters_dict, f)
        return

    #user related functions

    def check_user(self):
        
        #check if user in flat db. if not, add them
        if self.user not in self.chatters_dict:
            self.chatters_dict[self.user] = { "permissions" : "none",
                                              "points" : 1,
                                              "comment_time" : int(time.time())
                                            }
            return

        else:
            return

    def add_points(self):
        """
        checks to see if points cooldown is active. if not, adds number of points set in config.py for one message
        """
        
        new_points = self.chatters_dict[self.user]['points'] + config.message_points
        if (self.comment_time - self.chatters_dict[self.user]["comment_time"]) >= config.points_cooldown:
            self.chatters_dict[self.user]["points"] = int(new_points)
            self.chatters_dict[self.user]["comment_time"] = int(time.time())
            return
        else:
            return

    #message handling

    def handle_message(self):
        
        self.check_user()
        self.add_points()

        if self.message[0] == '!':
            command = self.message[1:]
            if command in self.commands_dict:
                self.send_message(self.commands_dict[command])
            elif command not in self.commands_dict:
                pass
        else:
            pass

        self.write_chatters()
        return









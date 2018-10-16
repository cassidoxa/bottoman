import json
import time
import config

from config import points_cooldown, message_points

class MessageHandler:
    def __init__(self):
        
        self.chatters_dict = self.load_chatters('chatters.json')
        self.user = ''
        self.message = ''
        self.comment_time = 0

    def load_chatters(self, chatters_file):
        
        with open(chatters_file, 'r') as f:
            chatters = json.load(f)
        return chatters

    def write_chatters(self, chatters_dict):
        
        with open('chatters.json', 'w') as f:
            json.dump(chatters, f)
        return

    def check_user(self, user, chatters_dict):
        
        #check if user in flat db. if not, add them
        if user not in chatters_dict:
            chatters_dict[user] = { "permissions" : "none",
                                    "points" : "1",
                                    "comment_time" : int(time.time())
                                  }
        else:
            pass
        return chatters_dict

    def add_points(user, chatters_dict, comment_time):
        
        #add points and reset cooldown
        if int(time.time()) - comment_time > points_cooldown:
            chatters_dict[user]["points"] += message_points
            chatters_dict[user]["comment_time"] = int(time.time())
        else:
            pass
        return chatters_dict

    def handle_message(self, user, message, comment_time, chatters_dict):

        if message[0] == '!':
            command = message[1:]
            if command in self.command_dict:
                self.send_message(self.command_dict[command])
            elif command not in self.command_dict:
                pass
        else:
            pass #TODO implement the other stuff
        
        return

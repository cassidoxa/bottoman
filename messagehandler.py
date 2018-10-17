import json
import time
import re

import config

class MessageHandler:

    def __init__(self, user, message, comment_time, s):
        
        self.user = user.lower()
        self.permissions = ""
        self.message = message
        self.comment_time = comment_time
        self.s = s
        
        self.chatters_dict = self.load_chatters('chatters.json')
        self.commands_dict = self.load_commands('commands.json')
        
        self.dynamic_commands = ["changeuser", "addcommand", "delcommand"]
        self.permission_hierarchy = {"none" : 0, "mod" : 1, "admin" : 2}

    def send_message(self, message):

        messageTemp = f'PRIVMSG #{config.bot_channel} :{message}'
        self.s.send(f'{messageTemp}\r\n'.encode('utf-8'))
        print(f'Sent: {messageTemp}')

    #functions for loading and saving persistent data

    def load_chatters(self, chatters_file):
        
        with open(chatters_file, 'r') as f:
            chatters_dict = json.load(f)
        return chatters_dict

    def load_commands(self, command_file):
        with open(command_file, 'r') as f:
            command_dict = json.load(f)
        return command_dict

    def write_chatters(self):
        
        with open('chatters.json', 'w') as f:
            json.dump(self.chatters_dict, f)
        return

    #user related functions

    def add_user(self, added_user, init_points):
        self.chatters_dict[added_user] = { "permissions" : "none",
                                              "points" : init_points,
                                              "comment_time" : int(time.time())
                                            }
        return

    def check_user(self):
        """
        check if user in flat db. if not, add them. check and set user permissions for instance
        """
        if self.user not in self.chatters_dict:
            self.add_user(self.user, 1)
            return

        else:
            self.permissions = self.chatters_dict[self.user]["permissions"]
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

    def change_permissions(self, changed_user, new_permissions):
        if new_permissions not in self.permission_hierarchy.keys():
            self.send_message(f'"{new_permissions}" is not a valid user permissions setting')
            return
        else:
            pass
        
        if self.permissions == "admin":
            clean_user = changed_user.lower()
            if clean_user not in self.chatters_dict:
                self.add_user(clean_user, 0)
                self.chatters_dict[clean_user]["permissions"] = new_permissions
            else:
                self.chatters_dict[clean_user]["permissions"] = new_permissions
            self.send_message(f'{changed_user} had permissions changed to {new_permissions}')
            return
        else:
            return
    
    #command related functions

    def dynamic_command(self, command):
        """
        function for dynamic commands that mods and admins can run such as adding static commands, changing permissions, starting games, etc
        dynamic functions are hard coded with a progressive permissions check (0, 1, 2 for none, mod, admin etc) that does nothing
        and returns if user does not have sufficient permissions. dynamic commands must be added to self.dynamic_commands list to be used here
        """

        permissions = self.chatters_dict[self.user.lower()]["permissions"]
        if permissions == "none":
            return
        elif self.permission_hierarchy[permissions] >= 1:
            if command[1] == "addcommand":
                self.add_command(command[2], command[3])
            elif command[1] == "delcommand":
                self.del_command(command[2])
            elif command[1] == "changeuser":
                self.change_permissions(command[2], command[3])
        return

    def add_command(self, new_command, command_text):
        
        self.commands_dict[new_command] = str(command_text).lower()
        self.send_message(f'{self.user} added the command "!{new_command.lower()}"')
        self.write_commands()
        return

    def del_command(self, deleted_command):
  
        try:
            del self.commands_dict[deleted_command]
            self.send_message(f'{self.user} deleted the command "!{deleted_command.lower()}"')
            self.write_commands()
        except KeyError:
            self.send_message(f'"{deleted_command.lower()}" command does not exist')

        return      
        
    def write_commands(self):
        
        with open('commands.json', 'w') as f:
            json.dump(self.commands_dict, f)
        return
    
    #further parsing and message handling

    def handle_message(self):

        separate = re.split('[ !]', self.message, 3)     
        self.check_user()
        self.add_points()

        if self.message[0] == '!':
            command = self.message[1:].lower()
            if separate[1] in self.dynamic_commands:
                self.dynamic_command(separate)
            elif command in self.commands_dict:
                self.send_message(self.commands_dict[command])
            elif command not in self.commands_dict:
                pass
        else:
            pass
        
        print(f'{self.user} wrote: {self.message} at {self.comment_time}')
        self.write_chatters()
        return









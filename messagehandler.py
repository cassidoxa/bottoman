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

        self.dynamic_commands = ["changeuser",
                                 "addcommand",
                                 "delcommand",
                                 "commands",
                                 "points",
                                 "give",
                                 "take",
                                 "rewards",
                                 "addreward",
                                 "delreward",
                                 "spend"]

        self.permission_hierarchy = {"none" : 0, "games" : 1, "mod" : 2, "admin" : 3}

    def send_message(self, message):

        messageTemp = f'PRIVMSG #{config.bot_channel} :{message}'
        self.s.send(f'{messageTemp}\r\n'.encode('utf-8'))
        print(f'Sent: {messageTemp}')

    def whisper(self, user, message):

        self.send_message(f'/w {user} {message}')
        print(f'Whispered to {user} : {message}')

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
        """
        open chatters db and write changes
        should only call this function at the end of every message handling cycle to avoid extraneous writes
        """

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
        the function for an admin to give a user a custom amount of points is give_points
        """

        new_points = self.chatters_dict[self.user]['points'] + config.message_points
        if (self.comment_time - self.chatters_dict[self.user]["comment_time"]) >= config.points_cooldown:
            self.chatters_dict[self.user]["points"] = int(new_points)
            self.chatters_dict[self.user]["comment_time"] = int(time.time())
            return
        else:
            return

    def get_points(self):
        """
        makes the bot send a message telling user how many points they have
        """

        "send message to chat telling user how many points they have"
        self.send_message(f'{self.user}, you have {self.chatters_dict[self.user]["points"]} points')

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

    def give_points(self, user, added_points):

        if user in self.chatters_dict.keys():
            new_total = self.chatters_dict[user]["points"] + int(added_points)
            self.chatters_dict[user]["points"] = new_total
            self.send_message(f'{self.user} gave {user} {added_points} points')

        elif user not in self.chatters_dict.keys():
            self.add_user(user, added_points)

        return

    def take_points(self, user, removed_points):

        if user in self.chatters_dict.keys():
            new_total = self.chatters_dict[user]["points"] - int(removed_points)
            if new_total < 0:
                self.chatters_dict[user]["points"] = 0
            else:
                self.chatters_dict[user]["points"] = new_total

            self.send_message(f'{self.user} took {removed_points} points from {user}. {user} now has {self.chatters_dict[user]["points"]} points.')

        elif user not in self.chatters_dict.keys():
            return

        return

    #command related functions
    #the !bot command is a static command in the db that can be overwritten but has an initial message about bottoman

    def dynamic_command(self, command):
        """
        run commands that either have dynamic output or change some bot/user data. checks for correct permissions before running
        all dynamic commands except for games are hardcoded here and must be in the self.dynamic_commands list
        at the top of this module
        """

        permissions = self.chatters_dict[self.user.lower()]["permissions"]

        if command[1] == "points":
            self.get_points()
        elif command[1] == "rewards":
            self.list_rewards()
        elif command[1] == "spend":
            self.spend_points(command[2:])
        elif command[1] == "commands":
            self.list_commands()
        elif command[1] == "addcommand" and self.permission_hierarchy[permissions] >= 2:
            self.add_command(command[2], command[3])
        elif command[1] == "delcommand" and self.permission_hierarchy[permissions] >= 2:
            self.del_command(command[2])
        elif command[1] == "changeuser" and self.permission_hierarchy[permissions] >= 3:
            self.change_permissions(command[2], command[3])
        elif command[1] == "give" and self.permission_hierarchy[permissions] >= 3:
            self.give_points(command[2], command[3])
        elif command[1] == "take" and self.permission_hierarchy[permissions] >= 3:
            self.take_points(command[2], command[3])
        elif command[1] == "addreward" and self.permission_hierarchy[permissions] >= 3:
            self.add_reward(command[3], command[2])
        elif command[1] == "delreward" and self.permission_hierarchy[permissions] >= 3:
            self.delete_reward(command[2:])
        else:
            pass
        return

    def add_command(self, new_command, command_text):

        if new_command in self.dynamic_commands:
            self.send_message(f'"{new_command}" is a reserved command')
        else:
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

    def list_commands(self):
        """
        first make a string of static commands. dynamic commands that users can use(eg !points) will be hard coded at the beginning
        so the constructed string will start with a comma as such: ", "
        """

        commands_string = ""
        for command in self.commands_dict.keys():
            if command != "chat rewards":    
                commands_string += f', !{command}'

        self.send_message(f'Currently available commands are: !points, !spend,{commands_string}')
        return

    def write_commands(self):

        with open('commands.json', 'w') as f:
            json.dump(self.commands_dict, f)
        return

    #rewards functions
    #reward information is stored in commands db with the two-word key "chat rewards" so it can't be
    #overwritten by another command

    def list_rewards(self):
        """
        list currently available rewards in chat for users to see
        """
        if any(self.commands_dict["chat rewards"]) == False:
            self.send_message(f'No rewards currently available')
            return

        rewards_string = ""
        for reward, cost in self.commands_dict["chat rewards"].items():
            rewards_string += f'{reward} - {cost}, '
        self.send_message(rewards_string[0:-2])

    def add_reward(self, reward, cost):
        """
        add a reward to db that users can cash in points for. If reward exists, overwrite it.
        TODO: check for malformed command before accepting
        """
        self.commands_dict["chat rewards"][reward] = cost
        self.send_message(f'Reward added: {reward} - {cost}')
        self.write_commands()

    def delete_reward(self, reward):
        """
        check to see if the reward is in db then delete a reward from db and saves new db
        send message to chat about the deleted reward. function first manipulates the passed value to access dict key
        """
        try:
            deleted_reward = f'{reward[0]} {reward[1]}'
            del self.commands_dict["chat rewards"][deleted_reward]
            self.send_message(f'"{deleted_reward}" deleted')
            self.write_commands()
            return
        except KeyError:
            self.send_message(f'"{deleted_reward}" does not exist')

    def spend_points(self, reward):
        """
        let a user spend points on a reward. if insufficient points or mistyped reward, send a message telling the user.
        if sufficient points, send a message saying what the user bought and send a whisper to the channel owner.
        the value passed to this function is also manipulated and made into a useful string in desired_reward
        TODO: remove int coercions maybe when fixing add reward function
        """

        desired_reward = f'{reward[0]} {reward[1]}'
        
        try:
            reward_cost = int(self.commands_dict["chat rewards"][desired_reward])
        except KeyError:
            self.send_message(f'{self.user}, that reward does not exist')
            return
        
        user_points = int(self.chatters_dict[self.user]["points"])
        
        if user_points < reward_cost:
            self.send_message(f"{self.user}, you don't have enough points for {reward}")
            return

        points_spent = reward_cost
        self.chatters_dict[self.user]["points"] = user_points - reward_cost
        
        self.send_message(f'{self.user}, you spent {points_spent} on {desired_reward}. You now have {self.chatters_dict[self.user]["points"]} points.')
        purchase_whisper = f'{self.user} purchased "{desired_reward}"'        
        self.whisper(config.bot_channel, purchase_whisper)
        return

    #further parsing and message handling

    def handle_message(self):

        separate = re.split('[ !]', self.message, 3)
        self.check_user()
        self.add_points()

        if self.message[0] == "!":
            command = self.message[1:].lower()
            if separate[1] in self.dynamic_commands:
                self.dynamic_command(separate)
            elif separate[1] in self.commands_dict:
                self.send_message(self.commands_dict[command])
            elif separate[1] not in self.commands_dict:
                pass
        elif self.message[0] == "?":
            pass
        else:
            pass

        print(f'{self.user} wrote: {self.message} at {self.comment_time}')
        self.write_chatters()
        return "yeah"



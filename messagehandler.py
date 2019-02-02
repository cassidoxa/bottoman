import requests
import re
import sys

import config



class MessageHandler:

    def __init__(self, msg_info, active_game, points_toggle, dbmgr):

        self.user = msg_info[0]
        self.user_display = ''
        self.message = msg_info[1] 
        self.message_time = msg_info[2]
        self.active_game = active_game 
        self.points_toggle = points_toggle
        self.dbmgr = dbmgr

        self.permissions = ''
        self.permission_hierarchy = {"none" : 0, "games" : 1, "mod" : 2, "admin" : 3}
        self.games_list = ["gtbk", "meateo"]
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
                                 "buy",
                                 "setreminder",
                                 "shutdown",
                                 "pointson",
                                 "pointsoff"]

        self.bot_instructions = [[], {'sendmsg': None, 'sendwhisper': None}]        

        

    def set_reminder(self, reminder_msg):
        """
        chat command that will change or disable a regular reminder message
        """
        if reminder_msg[0] == 'none':
            self.dbmgr.write("UPDATE config SET config_text=? WHERE config_option=?", ('none', 'reminder_message'))
            self.send_message(f'Reminder disabled')
            return
        else:
            pass

        reminder_msg = ' '.join(reminder_msg).rstrip()

        self.dbmgr.write("UPDATE config SET config_text=? WHERE config_option=?", (reminder_msg, 'reminder_message'))
        self.send_message("Reminder message set")
        return

    #functions for sending messages to chat and whispering.
    #these functions pass data to the main bottoman module to be sent/whispered

    def send_message(self, message):
        self.bot_instructions[1]['sendmsg'] = message

    def whisper(self, recipient, whisper):
        self.bot_instructions[1]['sendwhisper'] = (recipient, whisper)

    #user related functions

    def add_user(self, user_id, user_lower, user_display, init_points=1):
        self.dbmgr.write("INSERT INTO chatters VALUES (?,?,?,?,?,?)", (user_id, user_lower, user_display, 'none', init_points, self.message_time)) 
        return

    def get_user_id_display(self, user):
        """
        uses twitch's API to get a user's token with their (case insensitive)
        user name
        """

        print(f'Ran get_user_id_display() - debug')
        token = config.token[6:]
        header = {"Authorization": f'Bearer {token}'}
        response = requests.get(f'https://api.twitch.tv/helix/users?login={user}', headers=header).json()
        
        return (int(response['data'][0]['id']), response['data'][0]['display_name'])

    def check_user(self):
        """
        check if user in db. if not, retrieve twitch user id via API and add them or
        change name if there's a duplicate id. check and set user permissions
        for message being handled 
        """

        user_list = [user[0] for user in self.dbmgr.query("SELECT user_lower FROM chatters")]

        if self.user in user_list:
            self.permissions = self.dbmgr.query("SELECT permissions FROM chatters WHERE user_lower=?", (self.user,)).fetchone()[0]
            self.user_display = self.dbmgr.query("SELECT user_display FROM chatters WHERE user_lower=?", (self.user,)).fetchone()[0]
            return

        elif self.user not in user_list:
            user_id, self.user_display = self.get_user_id_display(self.user)
            user_id_list = [id[0] for id in self.dbmgr.query("SELECT user_id FROM chatters")]

            if user_id not in user_id_list:
                self.add_user(user_id, self.user, self.user_display)
                self.permissions = 'none'

            elif user_id in user_id_list:
                self.permissions = self.dbmgr.query("SELECT permissions FROM chatters WHERE user_id=?", (user_id,)).fetchone()[0]
                self.dbmgr.write("UPDATE chatters SET user_lower=?, user_display=? WHERE user_id=?", (self.user, self.user_display, user_id,))
                
        return

    def add_points(self):
        """
        checks to see if points cooldown is active. if not, adds number of points set in config.py for one message
        the function for an admin to give a user a custom amount of points is give_points
        """

        old_time = self.dbmgr.query("SELECT message_time FROM chatters WHERE user_lower=?", (self.user,)).fetchone()[0]

        if (self.message_time - old_time) >= config.points_cooldown:
            self.dbmgr.write("UPDATE chatters SET points = points + ?, message_time=? WHERE user_lower=?", (config.message_points, self.message_time, self.user))

        else:
            return

        return

    def get_points(self):
        """
        makes the bot send a message telling user how many points they have
        """
        
        points = self.dbmgr.query("SELECT points FROM chatters WHERE user_lower=?", (self.user,)).fetchone()[0]
        self.send_message(f'{self.user}, you have {points} points')
        return

    def change_permissions(self, changed_user, new_permissions):
        """change an existing user's permission or add user to db with appropriate permissions"""

        if new_permissions not in self.permission_hierarchy.keys():
            self.send_message(f'"{new_permissions}" is not a valid user permissions setting')
            return
        else:
            pass

        try:
            user_id, user_display = self.get_user_id_display(changed_user)
        except IndexError:
            self.send_message(f'Error adding new permissions for user "{changed_user}". Check spelling.')
            return

        user_id_list = [id[0] for id in self.dbmgr.query("SELECT user_id FROM chatters")]

        if user_id in user_id_list:
            self.dbmgr.write("UPDATE chatters SET permissions=? WHERE user_id=?", (new_permissions, user_id))
            self.send_message(f'{user_display} given "{new_permissions}" permissions')
        elif user_id not in user_id_list:
            self.add_user(user_id, user_display.lower(), user_display)
            self.dbmgr.write("UPDATE chatters SET permissions=? WHERE user_id=?", (new_permissions, user_id))
            self.send_message(f'{user_display} given "{new_permissions}" permissions')

        return

    def give_points(self, user, added_points):
        """
        admin chat command to give a user the specified number of points
        if the user doesn't exist in db, try to add them to db
        if user is not an active twitch account, send error message to chat
        """

        try:
            added_points = int(added_points)
        except ValueError:
            self.send_message(f'Error: Must use an integer number with the !give command')
            return

        if added_points <= 0:
            return

        try:
            user_id, user_display = self.get_user_id_display(user)
        except IndexError:
            self.send_message(f'Error giving points: Check spelling. This command is not case-sensitive')
            return

        database_check = self.dbmgr.query("SELECT * FROM chatters WHERE user_id=?", (user_id,)).fetchone()
        if database_check == None:
            self.add_user(user_id, user_display.lower(), user_display, added_points)
            self.send_message(f'Gave {user_display} {added_points} points')
            return
        else: 
            self.dbmgr.write("UPDATE chatters SET points= points + ? WHERE user_id=?", (added_points, user_id,))
            self.send_message(f'Gave {user_display} {added_points} points')

        return

    def take_points(self, user, removed_points):
        """Take specified number of points from existing user without allowing points to go below zero"""

        try:
            removed_points = int(removed_points)
        except ValueError:
            self.send_message(f'Error: Must use an integer with the !take command')
            return

        if removed_points <= 0:
            return

        try:
            user_id, user_display = self.get_user_id_display(user)
        except IndexError:
            self.send_message(f'Error removing points: Check spelling. This command is not case-sensitive')
            return

        current_points = self.dbmgr.query("SELECT points FROM chatters WHERE user_id=?", (user_id,)).fetchone()[0]

        if current_points == None:
            self.send_message(f'{user_display} hasn\'t chatted in here yet')
            return

        else:
            
            user = user_display
            new_points = current_points - removed_points

            if new_points >= 0:
                self.dbmgr.write("UPDATE chatters SET points=? WHERE user_id=?", (new_points, user_id,))
                self.send_message(f'{self.user_display} took {removed_points} from {user}. {user} now has {new_points}')
            elif new_points < 0:
                self.dbmgr.write("UPDATE chatters SET points=0 WHERE user_id=?", (user_id_display[0],))
                self.send_message(f'{self.user_display} took {removed_points} from {user}. {user} now has 0 points')

        return

    def ptoggle_on(self):
        """turns point toggle on. When toggle is on, users will earn points for sending chat messages"""

        self.bot_instructions[0].append("ptoggle on")
        return

    def ptoggle_off(self):
        """turns point toggle off. When toggle is off, users will not earn points for sending chat messages"""

        self.bot_instructions[0].append("ptoggle off")
        return

    #command related functions
    #the !bot command is a static text command in the db that can be overwritten but has an initial message about bottoman

    def dynamic_command(self, command):
        """
        run commands that either have dynamic output or change some bot/user data. checks for correct permissions before running.
        all dynamic commands except for games are hardcoded here and must be in the self.dynamic_commands list
        at the top of this module
        """

        permissions = self.permissions

        try:
            if command[1] == "points":
                self.get_points()
            elif command[1] == "rewards":
                self.list_rewards()
            elif command[1] == "buy":
                self.spend_points(command[2:])
            elif command[1] == "commands":
                self.list_commands()
            elif command[1] == "addcommand" and self.permission_hierarchy[permissions] >= 2:
                self.add_command(command[2], command[3])
            elif command[1] == "delcommand" and self.permission_hierarchy[permissions] >= 2:
                self.del_command(command[2])
            elif command[1] == "setreminder" and self.permission_hierarchy[permissions] >= 2:
                self.set_reminder(command[2:])
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
            elif command[1] == "pointson" and self.permission_hierarchy[permissions] >= 3:
                self.ptoggle_on()
            elif command[1] == "pointsoff" and self.permission_hierarchy[permissions] >= 3:
                self.ptoggle_off()
            elif command[1] == "shutdown" and self.permission_hierarchy[permissions] >= 3:
                self.bot_instructions[0].append(f'shutdown')
        except IndexError:
            self.send_message(f'Malformed command. Please try again')

        return

    def add_command(self, new_command, command_text):
        """Add a static text command to db"""
        
        command_list = [command[0] for command in self.dbmgr.query("SELECT command FROM commands")]
        new_command = new_command.lower()

        if new_command in self.dynamic_commands:
            self.send_message(f'"{new_command}" is a reserved command')
            return

        if new_command in command_list:
            self.dbmgr.write("UPDATE commands SET command=?, command_text=? WHERE command=?", (new_command, command_text, new_command))
            self.send_message(f'Added command !{new_command}')
        elif new_command not in command_list:
            self.dbmgr.write("INSERT INTO commands VALUES(?, ?)", (new_command, command_text,))
            self.send_message(f'Added command !{new_command}')

        return

    def del_command(self, deleted_command):
        """Delete a static text command from db"""

        command_list = [command[0] for command in self.dbmgr.query("SELECT command FROM commands")]
        deleted_command = deleted_command.lower()

        if deleted_command not in command_list:
            self.send_message(f'!{deleted_command} not found in commands database')
        elif deleted_command in command_list:
            self.dbmgr.write("DELETE FROM commands WHERE command=?", (deleted_command,))
            self.send_message(f'!{deleted_command} command deleted')
        
        return

    def list_commands(self):
        """
        first make a string of static commands. dynamic commands that users can use(eg !points) will be hard coded at the beginning
        so the constructed string will start with a comma as such: ", "
        """

        command_list = [command[0] for command in self.dbmgr.query("SELECT command FROM commands")]
        commands_string = ""
        reward_list = [reward[0] for reward in self.dbmgr.query("SELECT * FROM rewards")]
        
        if command_list == [] and reward_list == []:
            self.send_message(f'Available commands: !bot, !points')
        elif len(command_list) > 0 and reward_list == []:
            for command in command_list:
                commands_string += f', !{command}'
            self.send_message(f'Available commands: !points{commands_string}')
        else:
            for command in command_list:
                commands_string += f', !{command}'
            self.send_message(f'Available commands: !points, !rewards, !buy{commands_string}')

        return

    #rewards functions
    #reward information is stored in commands db with the two-word key "chat rewards" so it can't be
    #overwritten by another command

    def list_rewards(self):
        """
        list currently available rewards in chat for users to see
        """

        rewards_string = ""
        reward_list = [reward for reward in self.dbmgr.query("SELECT * FROM rewards").fetchall()]

        if reward_list == []:
            self.send_message(f'No rewards currently available')
        else:
            for reward, cost in reward_list:
                rewards_string += f'{reward} - {cost}, '
            self.send_message(rewards_string[0:-2])

        return

    def add_reward(self, new_reward, cost):
        """
        add a reward to db that users can cash in points for. If reward exists, overwrite it.
        check for malformed command before accepting
        """

        try:
            cost = int(cost)
        except ValueError:
            self.send_message('Malformed command. Please try again in the format "!addreward [cost in points] [reward]"')
            return

        new_reward = new_reward.rstrip()
        reward_list = [reward[0] for reward in self.dbmgr.query("SELECT reward FROM rewards")]
        
        if new_reward not in reward_list:
            self.dbmgr.write("INSERT INTO rewards VALUES (?, ?)", (new_reward, cost,))
            self.send_message(f'Added reward: "{new_reward} - {cost}"')
        elif new_reward in reward_list:
            self.dbmgr.write("UPDATE rewards SET reward=?, cost=? WHERE reward=?", (new_reward, cost, new_reward))
            self.send_message(f'Added reward: "{new_reward} - {cost}"')

        return
        
    def delete_reward(self, reward):
        """
        check to see if the reward is in db then delete a reward from db and saves new db
        send message to chat about the deleted reward. function first manipulates the passed value to access dict key
        """

        reward_list = [reward[0] for reward in self.dbmgr.query("SELECT reward FROM rewards")]

        if reward in reward_list:
            self.dbmgr.write("DELETE FROM rewards WHERE reward=?", (reward))
            self.send_message(f'"{reward}" deleted')
        elif reward not in reward_list:
            self.send_message(f'Error deleting reward. Check spelling. Command is case-sensitive')

        return

    def spend_points(self, reward):
        """
        let a user spend points on a reward. if insufficient points or mistyped reward, send a message telling the user.
        if sufficient points, send a message saying what the user bought and send a whisper to the channel owner.
        the value passed to this function is also manipulated and made into a useful string in desired_reward
        """
        
        desired_reward = ' '.join(reward)

        if desired_reward == '':
            self.send_message(f'Type !rewards to see available rewards. If you have enough !points, type the reward after !buy to purchase it')
            return
        

        #check if reward exists. If it does, get user points and see if they have enough.
        reward_list = [reward[0] for reward in self.dbmgr.query("SELECT * FROM rewards").fetchall()]

        if desired_reward not in reward_list:
            self.send_message(f'{self.user}, that reward does not exist. Check spelling and keep in mind that rewards are case sensitive')
            return
        elif desired_reward in reward_list:
            reward_cost = self.dbmgr.query("SELECT cost FROM rewards WHERE reward=?", (desired_reward,)).fetchone()[0]

        user_points = self.dbmgr.query("SELECT points FROM chatters WHERE user_lower=?", (self.user,)).fetchone()[0]

        if user_points < reward_cost:
            self.send_message(f'{self.user_display}, you don\'t have enough points for "{desired_reward}"')
            return

        elif user_points >= reward_cost:
            new_points = user_points - reward_cost
            purchase_whisper = f'{self.user_display} purchased "{desired_reward}"'

            self.dbmgr.write("UPDATE chatters SET points=? WHERE user_lower=?", (new_points, self.user))
            self.send_message(purchase_whisper)
            self.whisper(config.bot_channel, purchase_whisper)

        return
        
    #further parsing and message handling

    def handle_message(self):

        if self.user == 'twitch server':
            return

        separate = re.split('[ !]', self.message, 3)

        self.check_user()
        if self.points_toggle == True and config.message_points != 0:
            self.add_points()

        if self.message[0] == "!":

            command_list = [command[0] for command in self.dbmgr.query("SELECT * FROM commands").fetchall()]

            if separate[1] in self.dynamic_commands:
                self.dynamic_command(separate)
            elif separate[1] in command_list:
                command_text = self.dbmgr.query("SELECT command_text FROM commands WHERE command=?", (separate[1],)).fetchone()[0]
                self.send_message(command_text)
            elif separate[1] not in command_list:
                pass
        
#        elif self.message[0] == "?":
#            command = self.message[1:].lower()
#            if separate[1] == "start":
#                games.start_game(separate[2])
#                bot_instruction = 'start game'
#            elif separate[1] == "stop":
#                games.end_game
#                bot_instruction = "stop game"
#            elif separate[1] in self.games_list:
#                games.decide_winner(separate[2])
        
        print(f'{self.user} wrote: {self.message} at {self.message_time}') #debug, remove later
        self.bot_instructions[0].append("increment")
  
        return self.bot_instructions



import json

from bottoman import TwitchBot
import config

def check_admin():
    """
    check for an admin. If no admin user, ask for one and add to chatters db.
    uses a dictionary key in chatters db which cannot also be a twitch username to avoid looping through dictionary after admin is set
    """
    permissions_list = []
    with open('chatters.json', 'r+') as f:
        
        chatters_dict = json.load(f)
        if "has admin flag" in chatters_dict.keys() and chatters_dict["has admin flag"] == True:
            return
        else:
            pass
        
        admin_flag = False
        for user in chatters_dict:
                permissions_list.append(chatters_dict[user]["permissions"])
        
        if "admin" in permissions_list:
            chatters_dict["has admin flag"] = True
            pass
        else:
            while admin_flag == False:
                admin = input(f"This bot has no admin. Please enter the name of the admin twitch account (probably the channel you're using it on: ") 
                double_check = input(f'The admin account will be {admin}. Is this correct? (y/n): ')
                if double_check.lower() == "y":
                    chatters_dict[admin] = {"permissions": "admin", "points": 0, "comment_time": 0}
                    admin_flag = True
                elif double_check.lower() == "n":
                    continue
                else:
                    print(f"Didn't undertand answer. Please enter 'y' or 'n' to confirm admin username\n")
                    continue
        f.seek(0)
        json.dump(chatters_dict, f)
        f.truncate()
    return
                
               

#initialize bot, join room, load commands, then send hello message
check_admin()
bottoman = TwitchBot()
bottoman.join_room(bottoman.s)
bottoman.send_message(config.join_msg)

#check for admin user, ask for one if not present


bottoman.run_time()

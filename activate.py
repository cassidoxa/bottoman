import sqlite3
import requests

from bottoman import TwitchBot
import config

def get_user_id_display(user):
    """
    uses twitch's API to get a user's token with their (case insensitive)
    user name
    """

    token = config.token[6:]
    header = {"Authorization": f'Bearer {token}'}
    response = requests.get(f'https://api.twitch.tv/helix/users?login={user}', headers=header).json()
    return (response['data'][0]['id'], response['data'][0]['display_name'])

def check_admin():
    """check for an admin. If no admin user, ask for one and add to chatters db."""

    conn = sqlite3.connect('db/bottoman.db')
    c = conn.cursor()

    permissions_list = [i[0] for i in c.execute("SELECT permissions FROM chatters").fetchall()]

    if 'admin' in permissions_list:
        return

    else:
        admin_flag = False
        while admin_flag == False:
            admin = input(f"This bot has no admin. Please enter the name of your twitch channel you'll use it on: ") 
            double_check = input(f'The admin account will be {admin}. Is this correct? (y/n): ')
            if double_check.lower() == "y":
                user_id, name = get_user_id_display(admin)
                c.execute("INSERT INTO chatters VALUES (?,?,?,?,?,?)", (user_id, name.lower(), name, 'admin', 1, 0,))
                conn.commit()
                conn.close()
                admin_flag = True
            elif double_check.lower() == "n":
                continue
            else:
                print(f"Please try again.")
                continue

    return

#check for admin, initialize bot, join room, send hello message
check_admin()
bottoman = TwitchBot()
bottoman.join_room(bottoman.s)
bottoman.send_message(config.join_msg)

bottoman.run_time()

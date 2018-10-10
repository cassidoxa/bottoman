import json

from bottoman import TwitchBot
import config

#initialize bot, join room, load commands, then send hello message

bottoman = TwitchBot()
bottoman.join_room(bottoman.s)
bottoman.send_message(config.join_msg)

bottoman.run_time()

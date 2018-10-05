from bottoman import TwitchBot
import config

#initialize bot, join room, send hello message

bottoman = TwitchBot()
bottoman.join_room(bottoman.s)
bottoman.send_message(config.join_msg)

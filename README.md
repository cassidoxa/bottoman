<h1>Overview</h1>

Bottoman is a self hosted twitch bot that allows you to set simple commands in the format !command, set a reminder message that posts to chat after a certain number of minutes or chat messages, let users earn points that they can spend on rewards you choose, and play chat games. It's written in python as a script you run on your own computer when you want it to be active in chat.

<h1>Setup</h1>

Running bottoman requires python 3.6 or above, its own twitch account, and an oauth key that acts like a password for the bot and lets it log into your chat.

<b>Step 1: Download or clone this repository</b>

The first step is to download bottoman. You can use `git clone` or use the "clone or download button" on github to download a zip file. Extract the zip file into whatever directory you'd like (example for windows users: `C:\Users\Me\bottoman`).

<b>Step 2: Copy or rename config.py.sample</b>

Bottoman stores some configuration information in a file called `config.py`. Included in this repository is a file called `config.py.sample` with a sample configuration. First, make a copy of the sample and name it `config.py` or simply rename the sample. This file will require some manual editing on your part as you continue this setup:

<b>Step 3: Register your bot's twitch account, get an oauth token, and edit config.py</b>

Bottoman requires its own twitch account. Register a new account on twitch, you can choose any name you'd like, and log in. While logged in, open https://twitchapps.com/tmi/ in your browser, connect to twitch, and get your oauth token from the page. Make sure you have javascript enabled or the page won't work properly. Keep this token secret.

The token, bot name, and your channel that your bot must be entered into the appropriate variables config.py(`token, bot_name, bot_channel`) with a text editor. The token will be a random-looking text string the prefix "oauth". The other variables are appropriately named and easy to find. All variable must be contained in double quotation marks ("). Additionally, you can set a join message that the bot will send when it successfully joins your chat.

Below those variables you can adjust the amount of points users receive for sending messages to chat and a cooldown for when points are applied measured in seconds. The default values are one point and 80 seconds, which means that a user will get one point for sending a message, but will not recieve more points for additional messages until 80 seconds have passed. If you want to disable this feature, you can simply set the points variable to 0. Unlike the token, name, and channel, these values must be numbers and must not have double quotation marks around them.

The last section in config.py is for the reminder message function. You can tell the bot to automatically post a message that you've chosen after a certain number of messages in chat, a number of seconds, both, or neither. This message can be set with the !setreminder message (more on commands later). The default values are 100 messages and 1200 seconds (20 minutes), which means that the reminder will be posted after 1000 messages *or* 20 minutes, whichever comes first, at which point the message and time counter will be reset. If you want to disable one or both of these features, you can set these values to zero.

These variables related to chat points and reminder messages must be changed before the bot is started and can't currently be changed while the bot is running.

<h1>Running The Bot</h1>

After you've completed the previous steps, you'll be able to activate and run the bot. The file that starts the bot is activate.py. On Windows, you can simply double click this file if you've associated .py files with python when you installed it. On any other platform with python 3.6+, you can open a command line and run the bot from there. You can do this in Windows by pressing Ctrl + R and typing "cmd". Use the `cd` command followed by the directory that bottoman is in (example: `cd C:\User\Me\bottoman`). When you're in the directory, you can type `python activate.py` and the bot will start. 

<h1>Bot Permissions And Commands</h1>

There are four levels of permissions: admin, mod, games, and none. When you first run the bot, it will ask for your twitch user name and give you admin permissions, allowing you to run any command, before the bot joins your chat for the first time. Moderators can add and delete commands as well as change the reminder message and start games. People with the games permission can only start, stop, and record information about games. The permissions system is designed such that every level of permissions also has the permissions of the levels below it.

<h2>Admin Commands</h2>

<b>!changeuser</b> *(user)* *(permissions)* - Gives a user the desired permissions. *ex: !changuser cassidoxa mod*

<b>!addreward</b> *(cost)* *(reward)* - Adds a reward that will be displayed by the !rewards command. The first argument should be a number, the cost in points, and the second argument is a text description of the reward. *ex: !addreward 9999 One hour of play*

<b>!delreward</b> *(reward)* - Deletes a reward, removing it from the rewards that will be displayed by the !rewards command.

<b>!give</b> *(user)* *(points)* - Gives a user desired number of points.

<b>!take</b> *(user)* *(points)* - Subtracts points from a user's current total.

<b>!pointson</b> and <b>!pointsoff</b> - These commands will toggle points-earning on and off. Useful if you want to run the bot while you're not streaming.

<b>!shutdown</b> - Shuts the bot down. It will need to be manually restarted after using this command.

<h2>Moderator Commands</h2>

<b>!setreminder</b> *(reminder message)* - Sets the regular reminder message. Changing this to "none" will disable the reminder until it is changed to something else. *ex: !setreminder Feel free to join out discord server*

<b>!addcommand</b> *(command* *(command text)* - Adds a simple command that will return the command text when typed by anyone in chat.

<b>!delcommand</b> *(command)* - Removes an existing text command. Will not remove any commands listed here.

<h2>Game Commands</h2>

Placeholder

<h2>Commands Anyone Can Use</h2>

<b>!commands</b> - Lists all available commands

<b>!rewards</b> - Lists all available rewards and their cost in points

<b>!points</b> - Tells a user their current point total

<b>!spend</b> *(reward)* - If a user has enough points for the desired reward, sends a whisper to your twitch account reminding you of their selection and subtracts the cost from their point total. If the user has too few points, the bot tells them this and shows their point total



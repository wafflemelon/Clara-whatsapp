from yowsup.stacks import  YowStackBuilder
from .layer import MessageLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.env import YowsupEnv
from .classes import Bot

# Obtain password using `yowsup-cli registration -C COUNTRY_CODE -p PHONE_NUMBER -r sms`.
# Then: `yowsup-cli registration -C COUNTRY_CODE -p PHONE_NUMBER -R VERIFICATION_CODE`.
# This will return a base64 encoded password. DO NOT DECODE THIS, JUST PUT THAT AS PASSWORD
CREDENTIALS = ("phone", "password")

bot = Bot(prefix="owo!")

@bot.command("help", desc="get help", alias="?", unprefixed=True)
def help_(message):
    args = message.body.split()
    if len(args) > 1:
        try:
            res = bot.commands[args[1]].desc
        except IndexError:
            res = "Command '{}' not found!".format(args[1])
    else:
        res = "Use '? <command>' for help on a specific command\nUse {0.prefix}commands for a list of commands".format(bot)
    bot.layer.reply(message, res)


# Create the client 
stackBuilder = YowStackBuilder()

stack = stackBuilder\
    .pushDefaultLayers(True)\
    .push(MessageLayer)\
    .build()
    
# Set the bot as a parameter to the stack
stack.bot = bot
stack.setCredentials(CREDENTIALS)
   
# Send the connect signal
stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT)) 
 
# This runs the main loop
stack.loop() 
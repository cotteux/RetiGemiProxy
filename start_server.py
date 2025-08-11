from lxmfbot import LXMFBot
import ignition
bot = LXMFBot("testbot")

@bot.received
def echo_msg(msg):
    print(msg)
    response = ignition.request("gemini://"+str(msg.content))
    msg_final = (response.data())
    msg.reply(msg_final)

bot.run()

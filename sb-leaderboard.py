import discord, asyncio, time
from discord.ext import commands
import database_reader, passwords_and_tokens
import praw

bot_commands = None
probechannel = None
tor_server = None

reddit = praw.Reddit(client_id=passwords_and_tokens.reddit_id, client_secret=passwords_and_tokens.reddit_token,
                     user_agent="Lornebot 0.0.1")

def owner_only():
    def pred(ctx):
        if ctx.guild is None:
            return False
        if ctx.author.id == ctx.bot.owner_id:
            return True
    return commands.check(pred)

def get_redditor_name(name):
    return name.replace("/u/", "").replace("u/", "").split(" ")[0]

async def add_user(u, id):
    database_reader.add_user(get_redditor_name(u), id)


async def reset_leaderboard_internal():
    open("leaderboard.txt", "w").close()

async def post_leaderboard_internal(bot, channel):
    with open("leaderboard.txt", "a") as dat:
        msg = await bot.send_message(channel, "Waiting for refresh...")
        dat.write(msg.id + " " + msg.channel.id + "\n")

    await refresh_leaderboard()


async def refresh_leaderboard():
    returnstring = "**Leaderboard**\n\n"
    count = 0

    for name, flair in sorted(database_reader.gammas(), key=lambda x: x[1], reverse=True)[:50]:
        count += 1
        returnstring += str(count) + ". " + name.replace("_", "\\_") + ": " + str(flair) + "\n"

    returnstring += "\n*This Message will be refreshed to always be up-to-date*"

    with open("leaderboard.txt", "r") as dat:
        for line in dat.readlines():
            line = line.strip()
            if (not line == ""):
                msg, channel = line.split(" ")
                cha = client.get_channel(channel)
                m = await client.get_message(cha, msg)
                await client.edit_message(m, returnstring)

class Leaderboard():
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self): # no decorator needed, https://stackoverflow.com/questions/48038953/bot-event-in-a-cog-discord-py
        await refresh_leaderboard()
        await watch(self.bot)
        # SET probechannel and botcommands
        probechannel = client.get_channel("387401723943059460")
        bot_commands = client.get_channel("372168291617079296")
        tor_server = client.get_server("318873523579781132")

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True, pass_context=True)
    async def reset_leaderboard(self, ctx):
        await self.bot.say("Resetting leaderboard...")
        await reset_leaderboard_internal()

    @commands.command(hidden=True, pass_context=True)
    async def watch(self, ctx):
        await watch(self.bot)

    @commands.command(hidden=True, pass_context=True)
    async def restart(self, ctx):
        await self.bot.say("Restarting StatsBot")
        await self.bot.close()

    @commands.command(hidden=True, pass_context=True)
    async def post_leaderboard(self, ctx):
        await post_leaderboard_internal(self.bot, ctx.message.channel)
        await self.bot.say("Done!")
    
def setup(bot):
    bot.add_cog(Leaderboard(bot))

async def watch(bot):
    lasttime = time.time()
    while True:
        nextit = set(tor_server.members)
        print(".")
        for u in nextit:
            await add_user(u.display_name, u.id)

        gammas_changed = False
        for thing in database_reader.get_new_flairs(lasttime):
            gammas_changed = True
            await new_flair(bot, thing[0], thing[1], thing[2], thing[3])

        if gammas_changed:
            print("r", end="")
            await refresh_leaderboard()

        lasttime = time.time()
        await asyncio.sleep(10)


async def new_flair(bot, name, before, after, u):
    mention = (await bot.get_user_info(u)).mention
    await bot.send_message(probechannel, name + " got from " + str(before) + " to " + str(after))
    if not before == 0:
        if before < 51 <= after:
            await bot.send_message(bot_commands, "Congrats to " + mention + " for their green flair!")
        if before < 101 <= after:
            await bot.send_message(bot_commands, "Teal flair? Not bad, " + mention + "!")
        if before < 251 <= after:
            await bot.send_message(bot_commands, mention + " got purple flair, amazing!")
        if before < 501 <= after:
            await bot.send_message(bot_commands,
                                      "Give it up for the new owner of golden flair, " + mention + "!")
        if before < 1001 <= after:
            await bot.send_message(bot_commands, "Holy guacamole, " + mention + " earned their diamond flair!")
        if before < 2501 <= after:
            await bot.send_message(bot_commands, "Ruby flair! " + mention + ", that is absolutely amazing!")
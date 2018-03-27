from discord.ext import commands
import passwords_and_tokens, inspect

description = '''A bot to show your ToR stats on the discord.'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ["sb-textcommands", "sb-graphs", "sb-admin", "sb-reactions", "sb-routines"]

bot = commands.Bot(command_prefix='!', description=description)

BOT_OWNER="256084554375364613" # TODO: Get owner from bot owner set in main file

def owner(ctx):
    if ctx.message.author.id == BOT_OWNER:
        return True
    return False

@bot.command(hidden=True)
@commands.check(owner)
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command(hidden=True)
@commands.check(owner)
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@commands.command(pass_context=True, hidden=True)
async def debug(self, ctx, *, code : str):
    """Evaluates code."""
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None

    env = {
        'bot': self.bot,
        'ctx': ctx,
        'message': ctx.message,
        'server': ctx.message.server,
        'channel': ctx.message.channel,
        'author': ctx.message.author
    }

    env.update(globals())

    try:
        result = eval(code, env)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        return

    await self.bot.say(python.format(result))



if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

bot.run(passwords_and_tokens.discord_token)
import logging
import traceback

from discord.ext import commands
import discord
from ..utils.permissions import is_owner, BOT_OWNERS


class Handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logging.info(
            f"{ctx.author.display_name} ran {ctx.prefix}{ctx.invoked_with} "
            f"with message: {ctx.message.content}."
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logging.warn(
            f"{ctx.author.display_name} ran {ctx.prefix}{ctx.invoked_with}"
            f"with message: {ctx.message.content} and had the error: "
            f"{traceback.format_exception(type(error), error, error.__traceback__)}"
        )

        signature = f"{ctx.prefix}{ctx.invoked_with} {ctx.command.signature}"
        if isinstance(error, commands.ConversionError):
            await ctx.send(
                f"Oops looks like something couldn't be converted to {error.converter}"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'Looks like you missed the required argument "{error.param}". '
                f"Here's the signature of the command to help you out: `{signature}`."
            )
        elif isinstance(error, commands.ArgumentParsingError):
            if isinstance(error, commands.UnexpectedQuoteError):
                await ctx.send(
                    (
                        "Check your quotes! "
                        "I think you dropped one into your arguments on accident..."
                    )
                )
            elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                await ctx.send(
                    "Quotes need their space too. "
                    "No literally a space character right after it!"
                )
            elif isinstance(error, commands.ExpectedClosingQuoteError):
                await ctx.send("Check your quotes! I think you lost one.")
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, commands.BadArgument):
                return
            elif isinstance(error, commands.BadUnionArgument):
                await ctx.send(
                    f"I couldn't turn {error.param} into any of `{error.converters}`."
                )
            elif isinstance(error, commands.TooManyArguments):
                await ctx.send(
                    "You gave this command too many arguments. "
                    "It's too full to take all those arguments!"
                )
        elif isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.PrivateMessageOnly):
                await ctx.send("This command is only for private messages only, silly.")
            elif isinstance(error, commands.NoPrivateMessage):
                await ctx.send("This command doesn't work for private messages, silly.")
            elif isinstance(error, commands.NotOwner) or isinstance(error):
                await ctx.send("Nu-uh, that command is for owners only.")
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send(
                    (
                        "Sorry this command is off limits for you!"
                        f"You don't got the {error.missing_perms} perms."
                    )
                )
            elif isinstance(error, commands.BotMissingPermissions):
                await ctx.send(
                    (
                        "Sorry, looks like I can't do that!"
                        f"I don't have the {error.missing_perms} perms."
                    )
                )
            elif isinstance(error, commands.MissingRole):
                await ctx.send(
                    f'You need the very special role "{error.missing_role}".'
                )
            elif isinstance(error, commands.MissingAnyRole):
                await ctx.send(f'You need one of these roles "{error.missing_roles}".')
            elif isinstance(error, commands.BotMissingRole):
                await ctx.send(f'I need the very special role "{error.missing_role}".')
            elif isinstance(error, commands.BotMissingAnyRole):
                await ctx.send(f'You need one of these roles "{error.missing_roles}".')
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(
                    "You can't use this command for another "
                    f"{error.retry_after} seconds."
                )
            elif isinstance(error, commands.NotOwner) or is_owner in ctx.command.checks:
                await ctx.send("You aren't the owner, silly.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("That command is disabled.")
        elif isinstance(error, commands.ExtensionError):
            if isinstance(error, commands.ExtensionAlreadyLoaded):
                await ctx.send(
                    f"Oops, the extension {error.name} has already been loaded."
                )
            elif isinstance(error, commands.ExtensionNotLoaded):
                await ctx.send(f"The extension {error.name} could not be loaded.")
            elif isinstance(error, commands.NoEntryPointError):
                await ctx.send(
                    f"Oops, the extension {error.name} had an error "
                    "while being loaded."
                )
            elif isinstance(error, commands.ExtensionFailed):
                await ctx.send(
                    f"Well something went wrong in loading the extension {error.name}. "
                    "Luckily it's not my fault. Unfortunately that means its your's."
                )
        elif isinstance(error, commands.CommandInvokeError):
            maintainer_id = None
            for owner_id in BOT_OWNERS:
                owner = await self.bot.fetch_user(owner_id)
                if owner.status == discord.Status.online:
                    maintainer_id = owner_id
                    break
                elif owner.status == discord.Status.idle and maintainer_id is not None:
                    maintainer_id = owner_id

            contact_message = "Contact a maintainer for help."
            if maintainer_id is not None:
                contact_message = (
                    f"It seems like <@{maintainer_id}> is online, "
                    "and may be able to help you."
                )

            await ctx.send(
                (
                    "Looks like I had a problem while running that command... "
                    f"{contact_message}"
                )
            )
            logging.info(f"Message: {error.message}")
        else:
            await ctx.send("Well I don't really know how to handle this error...")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        logging.info(f"Finished running {ctx.prefix}{ctx.invoked_with}")


def setup(bot):
    bot.add_cog(Handlers(bot))

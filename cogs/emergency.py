import discord
from discord.ext import commands
import traceback
import inspect
import re


class EmergencyCog:
    """This is the emergency cog.
    It's a lightweight version of admin cog,
    in case something goes wrong with admin cog (and I get locked out)."""

    def __init__(self, bot):
        self.bot = bot
        self.last_eval_result = None
        self.previous_eval_code = None

    @commands.is_owner()
    @commands.command(name='eexit', hidden=True)
    async def _exit(self, ctx):
        """Shuts down AveBot, owner only."""
        await ctx.send(":wave: Exiting AveBot, goodbye!")
        await self.bot.logout()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def eload(self, ctx, ext: str):
        """Loads a cog, owner only."""
        try:
            self.bot.load_extension("cogs." + ext)
        except:
            await ctx.send(f':x: Cog loading failed, traceback: ```\n{traceback.format_exc()}\n```')
            return
        self.bot.log.info(f'Loaded ext {ext}')
        await ctx.send(f':white_check_mark: `{ext}` successfully loaded.')

    @commands.is_owner()
    @commands.command(name='eeval', hidden=True)
    async def _eval_em(self, ctx, *, code: str):
        """Evaluates some code (Owner only)"""
        try:
            code = code.strip('` ')

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'server': ctx.guild,
                'guild': ctx.guild,
                'channel': ctx.message.channel,
                'author': ctx.message.author,

                # modules
                'discord': discord,
                'commands': commands,

                # utilities
                '_get': discord.utils.get,
                '_find': discord.utils.find,

                # last result
                '_': self.last_eval_result,
                '_p': self.previous_eval_code,
            }
            env.update(globals())

            self.bot.log.info(f"Evaling {repr(code)}:")
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result

            if result is not None:
                self.last_eval_result = result

            self.previous_eval_code = code

            sliced_message = await self.bot.slice_message(repr(result), prefix="```", suffix="```")
            for msg in sliced_message:
                await ctx.send(msg)
        except:
            sliced_message = await self.bot.slice_message(traceback.format_exc(), prefix="```", suffix="```")
            for msg in sliced_message:
                await ctx.send(msg)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def esh(self, ctx, *, command: str):
        """Runs a command on shell."""
        command = command.strip('`')
        tmp = await ctx.send(f'Running `{command}`...')
        self.bot.log.info(f"Running {command}")
        shell_output = await self.bot.async_call_shell(command)
        shell_output = f"\"{command}\" output:\n\n{shell_output}"
        self.bot.log.info(shell_output)
        sliced_message = await self.bot.slice_message(shell_output, prefix="```", suffix="```")
        if len(sliced_message) == 1:
            await tmp.edit(content=sliced_message[0])
            return
        await tmp.delete()
        for msg in sliced_message:
            await ctx.send(msg)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def epull(self, ctx, auto=False):
        """Does a git pull (Owner only)."""
        tmp = await ctx.send('Pulling...')
        git_output = self.bot.call_shell("git pull")
        await tmp.edit(content=f"Pull complete. Output: ```{git_output}```")
        bot_activity = discord.Game(
            name=f"{self.bot.config['base']['prefix']}help | "
                 f"{self.bot.get_git_revision_short_hash()}")
        await self.bot.change_presence(activity=bot_activity)
        if auto:
            cogs_to_reload = re.findall('cogs/([a-z]*).py[ ]*\|', git_output)
            for cog in cogs_to_reload:
                try:
                    self.bot.unload_extension("cogs." + cog)
                    self.bot.load_extension("cogs." + cog)
                    self.bot.log.info(f'Reloaded ext {cog}')
                    await ctx.send(f':white_check_mark: `{cog}` successfully reloaded.')
                except:
                    await ctx.send(f':x: Cog reloading failed, traceback: ```\n{traceback.format_exc()}\n```')
                    return

    @commands.is_owner()
    @commands.command(hidden=True)
    async def eunload(self, ctx, ext: str):
        """Unloads a cog, owner only."""
        self.bot.unload_extension("cogs." + ext)
        self.bot.log.info(f'Unloaded ext {ext}')
        await ctx.send(f':white_check_mark: `{ext}` successfully unloaded.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def ereload(self, ctx, ext="_"):
        """Reloads a cog, owner only."""
        if ext == "_":
            ext = self.lastreload
        else:
            self.lastreload = ext

        try:
            self.bot.unload_extension("cogs." + ext)
            self.bot.load_extension("cogs." + ext)
        except:
            await ctx.send(f':x: Cog reloading failed, traceback: ```\n{traceback.format_exc()}\n```')
            return
        self.bot.log.info(f'Reloaded ext {ext}')
        await ctx.send(f':white_check_mark: `{ext}` successfully reloaded.')


def setup(bot):
    bot.add_cog(EmergencyCog(bot))

import discord
from discord.ext import commands

import time
import datetime
import socket
import os
import psutil


class Basic:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())

    @commands.command(aliases=['about'])
    async def info(self, ctx):
        """Returns bot's info."""
        local_time = str(datetime.datetime.now()).split('.')[0]
        total_guild_count = len(self.bot.guilds)
        total_unique_user_count = len(list(set(self.bot.get_all_members())))
        owner = str(self.bot.bot_info.owner)

        mem_bytes = self.process.memory_full_info().rss
        mem_mb = round(mem_bytes / 1024 / 1024, 2)
        cpu_usage = round(self.process.cpu_percent() / psutil.cpu_count(), 2)

        uptime = self.bot.get_relative_timestamp(
            time_from=datetime.datetime.utcfromtimestamp(self.bot.start_time))

        em = discord.Embed(color=0xDAB420)

        em.add_field(name="Git Hash",
                     value=self.bot.get_git_revision_short_hash())
        em.add_field(name="Last git message",
                     value=self.bot.get_git_commit_text())
        em.add_field(name="Hostname", value=socket.gethostname())
        em.add_field(name="Guild count", value=total_guild_count)
        em.add_field(name="Unique users", value=total_unique_user_count)
        em.add_field(name="Local Time", value=local_time)
        em.add_field(name="RAM Usage", value=f"{mem_mb}MiB")
        em.add_field(name="CPU Percentage", value=f"{cpu_usage}%")
        em.add_field(name="Uptime", value=uptime)
        em.add_field(name="Owner", value=owner)
        em.add_field(name="Invite", value="https://bot.ave.zone/add")

        em.set_author(name='AveBot v3', icon_url='https://s.ave.zone/c7d.png')
        await ctx.send(embed=em)

    @commands.command(aliases=['addavebot'])
    async def invite(self, ctx):
        """Gives a link that can be used to add AveBot."""
        inviteurl = discord.utils.oauth_url(self.bot.user.id)
        await ctx.send(f"You can use the following link to add AveBot "
                       f"to your server:\n<{inviteurl}>")

    @commands.command()
    async def hello(self, ctx):
        """Says hello. Duh."""
        await ctx.send(f"Hello {ctx.message.author.mention}!")

    @commands.command(hidden=True)
    async def dab(self, ctx):
        """Fuck nev"""
        await ctx.send("<:lunacdab:419587460423614464>")

    @commands.command()
    async def ginvite(self, ctx, discordid: int):
        """Generates a discord invite link."""
        inviteurl = discord.utils.oauth_url(discordid)
        await ctx.send(f"<{inviteurl}>")

    @commands.command()
    async def servercount(self, ctx):
        """Returns the amount of servers AveBot is in."""
        total_guild_count = len(self.bot.guilds)
        total_user_count = len(list(self.bot.get_all_members()))
        total_unique_user_count = len(list(set(self.bot.get_all_members())))
        await ctx.send(f"AveBot is in {total_guild_count} servers with "
                       f"{total_user_count} total users "
                       f"({total_unique_user_count} unique).")

    @commands.command(aliases=['p'])
    async def ping(self, ctx):
        """Shows ping values to discord.

        RTT = Round-trip time, time taken to send a message to discord
        GW = Gateway Ping"""
        before = time.monotonic()
        tmp = await ctx.send('Calculating ping...')
        after = time.monotonic()
        rtt_ms = (after - before) * 1000
        gw_ms = self.bot.latency * 1000

        message_text = f":ping_pong: rtt: `{rtt_ms:.1f}ms`, `gw: {gw_ms:.1f}ms`"
        self.bot.log.info(message_text)
        await tmp.edit(content=message_text)

    @commands.guild_only()
    @commands.command(aliases=['serverinfo', 'guildinfo', 'ginfo'])
    async def sinfo(self, ctx):
        """Shows info about the current server."""
        current_guild = ctx.guild
        em = discord.Embed(
            title=f"Server info of {current_guild.name} ({current_guild.id})")

        # All this effort for luna memes
        region_replace = {"us-west": ":flag_us: US West",
                          "us-east": ":flag_us: US East",
                          "us-south": ":flag_us: US South",
                          "us-central": ":flag_us: US Central",
                          "eu-west": ":flag_eu: EU West",
                          "eu-central": ":flag_eu: EU Central",
                          "singapore": ":flag_si: Singapore",
                          "london": ":flag_uk: London, UK",
                          "sydney": ":flag_au: Sydney, AU",
                          "amsterdam": ":flag_nl: Amsterdam, NL",
                          "frankfurt": ":flag_de: Frankfurt, DE",
                          "brazil": "<:lunacdab:419587460423614464> Brazil",
                          "hongkong": ":flag_hk: Hong Kong",
                          "russia": ":flag_ru: Russia",
                          "vip-us-east": ":flag_us: VIP US East",
                          "vip-us-west": ":flag_us: VIP US West",
                          "vip-amsterdam": ":flag_nl: VIP Amsterdam, NL"}

        region_text = str(current_guild.region)
        region_text = (region_replace[region_text] if
                       region_text in region_replace else region_text)

        em.add_field(name="User Count", value=current_guild.member_count)
        em.add_field(name="Region", value=region_text)
        em.add_field(name="Owner", value=current_guild.owner)
        em.add_field(name="Verification Level",
                     value=current_guild.verification_level)
        humanized_created = self.bot.get_relative_timestamp(
            time_from=current_guild.created_at,
            humanized=True,
            include_from=True)
        em.add_field(name="Created at", value=humanized_created)

        em.set_thumbnail(url=current_guild.icon_url)
        await ctx.send(embed=em)

    @commands.command(aliases=['contact'])
    async def feedback(self, ctx, *, contact_text: str):
        """Contacts developers with a message."""
        em = discord.Embed(description=contact_text)

        author_name = f"{ctx.message.author} ({ctx.message.author.id}) "
        author_name += (f"on \"{ctx.channel.name}\" at \"{ctx.guild.name}\""
                        if ctx.guild else "through DMs")

        em.set_author(name=author_name, icon_url=ctx.message.author.avatar_url)

        await self.bot.support_channel.send(embed=em)

        em = discord.Embed(title='Feedback sent!',
                           description='Your message has been delivered.')
        await ctx.send(embed=em)

    @commands.command(aliases=['userinfo', 'whoami', 'profile'])
    async def uinfo(self, ctx, *, user: discord.User = None):
        """Shows info about the user.

        info: returns info about the user who ran the command
        uinfo <mention/name>: returns info about the mentioned user"""

        if user is None:
            user = ctx.author

        if ctx.guild:
            maybe_member = ctx.guild.get_member(user.id)
            if maybe_member:
                user = maybe_member

        embed = discord.Embed(title=f"User Info of {str(user)}")

        if (user.avatar != ""):
            embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"UserID: {user.id}")

        humanized_discord = self.bot.get_relative_timestamp(
            time_from=user.created_at, humanized=True, include_from=True)
        embed.add_field(name="Joined Discord", value=humanized_discord)
        if ctx.guild and maybe_member:
            humanized_guild = self.bot.get_relative_timestamp(
                time_from=user.joined_at, humanized=True, include_from=True)
            embed.add_field(name="Joined Guild", value=humanized_guild)
            embed.add_field(name="Status", value=str(user.status))
        if user.activity:
            embed.add_field(name=user.activity.state, value=user.activity.name)
        is_bot_display = ":white_check_mark:" if user.bot else ":x:"
        embed.add_field(name="Is bot", value=is_bot_display)

        await ctx.send(embed=embed)

    @commands.command(aliases=['getavatar'])
    async def avatar(self, ctx, *, user: discord.User = None):
        """Gets your or a user's avatar.

        avatar <mention/name>: returns avatar of the mentioned user"""

        if user is None:
            user = ctx.author

        if ctx.guild:
            maybe_member = ctx.guild.get_member(user.id)
            if maybe_member:
                user = maybe_member

        if user.avatar:
            await ctx.send(f"{ctx.author.mention}: {user.avatar_url}")
        else:
            await ctx.send(f"{ctx.author.mention}: No user or avatar")


def setup(bot):
    bot.add_cog(Basic(bot))

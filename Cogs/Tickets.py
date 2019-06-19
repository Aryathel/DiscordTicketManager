import discord
from discord.ext import commands
import datetime
import yaml
import json
import re
import string
import os
import random
import asyncio

class TicketsCog(commands.Cog, name = ":tickets: Tickets (Server Only)"):
    def __init__(self, bot):
        self.bot = bot
        global support_id
        with open('./Config.yml') as file:
            support_id = yaml.load(file, Loader = yaml.Loader)['Tickets']['Support Channel ID']
        print("Loaded TicketsCog.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.log_tickets and not message.author.bot:
            for channel in self.bot.ticket_data:
                if channel['ID'] == message.channel.id:
                    datetime_obj = message.created_at - datetime.timedelta(hours=4)
                    with open(self.bot.ticket_folder + "/{}.txt".format(str(message.channel.id)), "a+") as file:
                        file.write("[{} EST] {}: {}\n".format(datetime_obj.strftime("%b-%d-%Y | %X"), message.author.name, message.content))

    def is_support_channel():
        async def check_channel(ctx):
            return ctx.channel.id == support_id
        return commands.check(check_channel)

    @commands.command(name='new', help = 'Open a new support ticket - please include a reason.')
    @commands.guild_only()
    @is_support_channel()
    async def new_ticket(self, ctx, *, reason = "No Reason"):
        await ctx.message.delete()
        await ctx.trigger_typing()
        found = False
        for role in ctx.guild.roles:
            if role.name == self.bot.support_role_name:
                found = True

        if found == False:
            if self.bot.use_timestamp:
                embed = discord.Embed(
                    title = "Failed to Create Ticket",
                    description = "This server does not have a `{}` role. Please contact a server administrator to solve this issue.".format(self.bot.support_role_name),
                    color = random.choice(self.bot.embed_colors),
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                )
            else:
                embed = discord.Embed(
                    title = "Failed to Create Ticket",
                    description = "This server does not have a `{}` role. Please contact a server administrator to solve this issue.".format(self.bot.support_role_name),
                    color = random.choice(self.bot.embed_colors)
                )
            if self.bot.show_command_author:
                embed.set_author(
                    name = ctx.author.name,
                    icon_url = ctx.author.avatar_url
                )
            embed.set_footer(
                text = self.bot.footer_text,
                icon_url = self.bot.footer_icon
            )
            msg = await ctx.send(embed = embed)
        else:
            already_exists = False
            for channel in self.bot.ticket_data:
                if channel['Creator'] == str(ctx.author):
                    already_exists = True
                    channel_ob = self.bot.get_channel(channel['ID'])
                    mention = channel_ob.mention

            if already_exists == True:
                if self.bot.use_timestamp:
                    embed = discord.Embed(
                        title = "Failed to Create Ticket",
                        description = "You already have a ticket open. Please use `{prefix}close` in the {mention} channel before opening a new ticket.".format(prefix=self.bot.prefix, mention=mention),
                        color = random.choice(self.bot.embed_colors),
                        timestamp = datetime.datetime.now(datetime.timezone.utc)
                    )
                else:
                    embed = discord.Embed(
                        title = "Failed to Create Ticket",
                        description = "You already have a ticket open. Please use `{prefix}close` in the {mention} channel before opening a new ticket.".format(prefix=self.bot.prefix, mention=mention),
                        color = random.choice(self.bot.embed_colors)
                    )
                if self.bot.show_command_author:
                    embed.set_author(
                        name = ctx.author.name,
                        icon_url = ctx.author.avatar_url
                    )
                embed.set_footer(
                    text = self.bot.footer_text,
                    icon_url = self.bot.footer_icon
                )
                msg = await ctx.send(embed = embed)
            else:
                support_role = discord.utils.get(ctx.guild.roles, name = self.bot.support_role_name)
                everyone_perms = discord.PermissionOverwrite(read_messages = False)
                viewer_perms = discord.PermissionOverwrite(read_messages = True)
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages = True),
                    support_role: discord.PermissionOverwrite(read_messages = True),
                    ctx.author: discord.PermissionOverwrite(read_messages = True)
                }
                if self.bot.ask_for_reason == True:
                    ch = await ctx.guild.create_text_channel('ticket-{}'.format(ctx.author.id), overwrites = overwrites, topic = "Reason: " + reason)
                else:
                    ch = await ctx.guild.create_text_channel('ticket-{}'.format(ctx.author.id), overwrites = overwrites)
                self.bot.ticket_data.append({"Creator": str(ctx.author), "ID": ch.id, "UserID": ctx.author.id})
                with open(self.bot.ticket_file, 'w+') as file:
                    file.write(json.dumps(self.bot.ticket_data, indent = 4, sort_keys = True))

                if self.bot.use_timestamp:
                    embed = discord.Embed(
                        title = "New Ticket",
                        description = self.bot.support_message,
                        color = random.choice(self.bot.embed_colors),
                        timestamp = datetime.datetime.now(datetime.timezone.utc)
                    )
                else:
                    embed = discord.Embed(
                        title = "New Ticket",
                        description = self.bot.support_message,
                        color = random.choice(self.bot.embed_colors)
                    )
                if self.bot.ask_for_reason == True:
                    embed.add_field(
                        name = "Reason for Ticket",
                        value = reason,
                        inline = False
                    )
                else:
                    embed.add_field(
                        name = "Reason",
                        value = "Please state your reason for opening this ticket.",
                        inline = False
                    )
                embed.set_author(
                    name = ctx.author.name,
                    icon_url = ctx.author.avatar_url
                )
                embed.set_footer(
                    text = self.bot.footer_text,
                    icon_url = self.bot.footer_icon
                )
                msg = await ch.send(embed = embed, content = support_role.mention + " " + ctx.author.mention)

                if self.bot.use_timestamp:
                    embed = discord.Embed(
                        title = "Ticket Created",
                        description = "Please head to {} to continue.".format(ch.mention),
                        color = random.choice(self.bot.embed_colors),
                        timestamp = datetime.datetime.now(datetime.timezone.utc)
                    )
                else:
                    embed = discord.Embed(
                        title = "Ticket Created",
                        description = "Please head to {} to continue.".format(ch.mention),
                        color = random.choice(self.bot.embed_colors)
                    )
                if self.bot.show_command_author:
                    embed.set_author(
                        name = ctx.author.name,
                        icon_url = ctx.author.avatar_url
                    )
                embed.set_footer(
                    text = self.bot.footer_text,
                    icon_url = self.bot.footer_icon
                )
                msg = await ctx.send(embed = embed)

            await asyncio.sleep(15)
            await msg.delete()

    @commands.command(name = 'close', help = 'Close an open support ticket - use in a ticket channel')
    @commands.guild_only()
    async def close_ticket(self, ctx):
        if self.bot.use_timestamp:
            await ctx.message.delete()

        okay_to_delete = False
        for ch in self.bot.ticket_data:
            if ctx.channel.id == ch['ID']:
                okay_to_delete = True

        if okay_to_delete == False:
            if self.bot.use_timestamp:
                embed = discord.Embed(
                    title = "Failed to Close Ticket",
                    description = "This command can only be used inside a ticket channel.",
                    color = random.choice(self.bot.embed_colors),
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                )
            else:
                embed = discord.Embed(
                    title = "Failed to Close Ticket",
                    description = "This command can only be used inside a ticket channel.",
                    color = random.choice(self.bot.embed_colors),
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                )
            if self.bot.show_command_author:
                embed.set_author(
                    name = ctx.author.name,
                    icon_url = ctx.author.avatar_url
                )
            embed.set_footer(
                text = self.bot.footer_text,
                icon_url = self.bot.footer_icon
            )
            await ctx.send(embed = embed)
        else:
            channel = ctx.channel
            author = ctx.author

            def check(m):
                if m.content.startswith("{prefix}confirm".format(prefix = self.bot.prefix)) and m.author == author and m.channel == channel:
                    return True
                else:
                    return False

            if self.bot.use_timestamp:
                embed = discord.Embed(
                    title = 'Are you sure?',
                    description = "To confirm, type `{prefix}confirm`.\nOnce confirmed, you cannot cancel this.\n*You have 10 seconds to respond.*".format(prefix = self.bot.prefix),
                    color = random.choice(self.bot.embed_colors),
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                )
            else:
                embed = discord.Embed(
                    title = 'Are you sure?',
                    description = "To confirm, type `{prefix}confirm`.\nOnce confirmed, you cannot cancel this.\n*You have 10 seconds to respond.*".format(prefix = self.bot.prefix),
                    color = random.choice(self.bot.embed_colors)
                )
            if self.bot.show_command_author:
                embed.set_author(
                    name = ctx.author.name,
                    icon_url = ctx.author.avatar_url
                )
            embed.set_footer(
                text = self.bot.footer_text,
                icon_url = self.bot.footer_icon
            )
            msg = await ctx.send(embed = embed)

            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 10.0)

            except asyncio.TimeoutError:
                if self.bot.use_timestamp:
                    embed = discord.Embed(
                        title = "Closing Cancelled",
                        color = random.choice(self.bot.embed_colors),
                        timestamp = datetime.datetime.now(datetime.timezone.utc)
                    )
                else:
                    embed = discord.Embed(
                        title = "Closing Cancelled",
                        color = random.choice(self.bot.embed_colors)
                    )
                if self.bot.show_command_author:
                    embed.set_author(
                        name = ctx.author.name,
                        icon_url = ctx.author.avatar_url
                    )
                embed.set_footer(
                    text = self.bot.footer_text,
                    icon_url = self.bot.footer_icon
                )
                await msg.edit(embed = embed)

            else:
                if self.bot.log_tickets:
                    for ticket in self.bot.ticket_data:
                        if ctx.channel.id == ticket['ID']:
                            try:
                                user_ob = await self.bot.fetch_user(ticket['UserID'])
                                if self.bot.use_timestamp:
                                    embed = discord.Embed(
                                        title = "Here is the record of your ticket in {}.".format(ctx.guild.name),
                                        color = random.choice(self.bot.embed_colors),
                                        timestamp = datetime.datetime.now(datetime.timezone.utc)
                                    )
                                else:
                                    embed = discord.Embed(
                                        title = "Here is the record of your ticket in {}.".format(ctx.guild.name),
                                        color = random.choice(self.bot.embed_colors)
                                    )
                                embed.set_footer(
                                    text = self.bot.footer_text,
                                    icon_url = self.bot.footer_icon
                                )
                                await user_ob.send(content = "Here is the record of your ticket in {}.".format(ctx.guild.name), file = discord.File(self.bot.ticket_folder + '/{}.txt'.format(str(ctx.channel.id))))
                                os.remove(self.bot.ticket_folder + '/{}.txt'.format(str(ctx.channel.id)))
                            except:
                                os.remove(self.bot.ticket_folder + '/{}.txt'.format(str(ctx.channel.id)))

                for ticket in self.bot.ticket_data:
                    if ticket['ID'] == ctx.channel.id:
                        self.bot.ticket_data.remove(ticket)

                with open(self.bot.ticket_file, 'w+') as file:
                    file.write(json.dumps(self.bot.ticket_data, indent = 4, sort_keys = True))

                await ctx.channel.delete(reason = 'Ticket Closed')

    @commands.command(name = 'rename', aliases = ['rename-ticket', 'rename_ticket'], help = "Set the name of the ticket")
    @commands.guild_only()
    async def rename_ticket(self, ctx, *, name = None):
        if self.bot.delete_commands:
            await ctx.message.delete()
        if name == None:
            if self.bot.use_timestamp:
                embed = discord.Embed(
                    title = "Failed to Rename Ticket",
                    description = "You must include a new ticket name.",
                    color = random.choice(self.bot.embed_colors),
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                )
            else:
                embed = discord.Embed(
                    title = "Failed to Rename Ticket",
                    description = "You must include a new ticket name.",
                    color = random.choice(self.bot.embed_colors)
                )
            if self.bot.show_command_author:
                embed.set_author(
                    name = ctx.author.name,
                    icon_url = ctx.author.avatar_url
                )
            embed.set_footer(
                text = self.bot.footer_text,
                icon_url = self.bot.footer_icon
            )
            await ctx.send(embed = embed)
        elif len(name) < 1 or len(name) > 100:
            if self.bot.use_timestamp:
                embed = discord.Embed(
                    title = "Failed to Rename Ticket",
                    description = "New ticet name must be between 1 and 100 characters, {} characters is an invalid number.".format(len(name)),
                    color = random.choice(self.bot.embed_colors),
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                )
            else:
                embed = discord.Embed(
                    title = "Failed to Rename Ticket",
                    description = "New ticet name must be between 1 and 100 characters, {} characters is an invalid number.".format(len(name)),
                    color = random.choice(self.bot.embed_colors)
                )
            if self.bot.show_command_author:
                embed.set_author(
                    name = ctx.author.name,
                    icon_url = ctx.author.avatar_url
                )
            embed.set_footer(
                text = self.bot.footer_text,
                icon_url = self.bot.footer_icon
            )
            await ctx.send(embed = embed)
        else:
            name = name.replace(" ", "-").lower()
            await ctx.channel.edit(name = re.sub(r'^\w-', '', name))

def setup(bot):
    bot.add_cog(TicketsCog(bot))

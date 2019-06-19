import discord
from discord.ext import commands
import datetime
import yaml
import os
import sys
import random
import json

with open("./Config.yml", 'r') as file:
    config = yaml.load(file, Loader = yaml.Loader)

bot = commands.AutoShardedBot(command_prefix=config['Prefix'], description="Heroicos_HM's Tickets Bot", case_insensitive = True)
bot.remove_command('help')

#Main Config
bot.TOKEN = config['TOKEN']
bot.prefix = config['Prefix']
bot.logs_channels = config['Log Channels']
bot.embed_colors = config['Embed Colors']
bot.footer_icon = config['Footer Icon URL']
bot.footer_text = config['Footer Text']
bot.online_message = config['Online Message']

#Options
bot.use_timestamp = config['Options']['Embed Timestamp']
bot.delete_commands = config['Options']['Delete Commands']
bot.show_command_author = config['Options']['Show Author']
bot.show_game_status = config['Options']['Game Status']['Active']
bot.game_to_show = config['Options']['Game Status']['Game']

#Ticket Config
bot.support_role_name = config['Tickets']['Support Role Name']
bot.ticket_folder = config['Tickets']['Ticket Log Folder']
if not os.path.exists(bot.ticket_folder):
    os.mkdir(os.path.abspath(bot.ticket_folder))
bot.ticket_file = config['Tickets']['Data File']
if os.path.isfile(bot.ticket_file):
    with open(bot.ticket_file, 'r') as file:
        bot.ticket_data = json.loads(file.read())
        if bot.ticket_data == None:
            bot.ticket_data = []
else:
    bot.ticket_data = []
bot.log_tickets = config['Tickets']['Log All Tickets']
bot.support_channel_id = config['Tickets']['Support Channel ID']
bot.support_message = config['Tickets']['New Ticket Message']
bot.ask_for_reason = config['Tickets']['Ask For Reason']

extensions = [
    'Cogs.General',
    'Cogs.Tickets'
]

for extension in extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print('Logged in as {0} and connected to Discord! (ID: {0.id})'.format(bot.user))
    if bot.show_game_status:
        game = discord.Game(name = bot.game_to_show.format(prefix = bot.prefix))
        await bot.change_presence(activity = game)
    if bot.use_timestamp:
        embed = discord.Embed(
            title = bot.online_message.format(username = bot.user.name),
            color = random.choice(bot.embed_colors),
            timestamp = datetime.datetime.now(datetime.timezone.utc)
        )
    else:
        embed = discord.Embed(
            title = bot.online_message.format(username = bot.user.name),
            color = random.choice(bot.embed_colors)
        )
    embed.set_footer(
        text = bot.footer_text,
        icon_url = bot.footer_icon
    )
    for log in bot.logs_channels:
        channel = bot.get_channel(log)
        await channel.send(content = None, embed = embed)

    bot.start_time = datetime.datetime.now(datetime.timezone.utc)

@bot.command(name='help')
@commands.guild_only()
async def dfs_help(ctx):
    if bot.delete_commands:
        await ctx.message.delete()
    if bot.use_timestamp:
        embed = discord.Embed(
            title = ":newspaper: Help",
            color = random.choice(bot.embed_colors),
            timestamp = datetime.datetime.now(datetime.timezone.utc)
        )
    else:
        embed = discord.Embed(
            title = ":newspaper: Help",
            color = random.choice(bot.embed_colors)
        )
    if bot.show_command_author:
        embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar_url
        )
    if bot.ask_for_reason:
        embed.add_field(
            name = bot.prefix + "new <reason>",
            value = "Creates a support ticket for the given reason.\nCan only be used in {mention}.".format(mention = bot.get_channel(bot.support_channel_id).mention),
            inline = False
        )
    else:
        embed.add_field(
            name = bot.prefix + "new",
            value = "Creates a support ticket.\nCan only be used in {mention}.".format(mention = bot.get_channel(bot.support_channel_id).mention),
            inline = False
        )
    embed.add_field(
        name = bot.prefix + "close",
        value = "Closes a ticket. Can only be used in a ticket channel.",
        inline = False
    )
    embed.add_field(
        name = bot.prefix + "rename",
        value = "Renames a ticket. Can only be used in a ticket channel.",
        inline = False
    )
    embed.add_field(
        name = bot.prefix + "uptime",
        value = "Returns the amount of time that the bot has been online.",
        inline = False
    )
    embed.add_field(
        name = bot.prefix + "ping",
        value = "Gets the ping times from the bot to the discord servers and back.",
        inline = False
    )
    embed.set_footer(
        text = bot.footer_text,
        icon_url = bot.footer_icon
    )

    await ctx.send(embed = embed)

bot.run(bot.TOKEN, bot = True, reconnect = True)

import discord
from discord.ext import commands, tasks, menus

import logging
import json
from datetime import datetime
from pathlib import Path
from asyncio import sleep as asleep
from time import sleep

# The event class that handles the message with embed and reactions
class Event(menus.Menu):
    def __init__(self, title, description):
        super().__init__(timeout=None, clear_reactions_after=True)

        self.title = title
        self.description = description
        self.agrees = []
        self.disagrees = []

    # Reaction check override
    def reaction_check(self, payload):
        if payload.event_type == 'REACTION_REMOVE':
            return False
        
        if payload.message_id != self.message.id:
            return False

        if payload.user_id == self.bot.user.id:
            return False

        return payload.emoji in self.buttons

    # Creates consistent embeds
    def create_embed(self):
        embed = discord.Embed(title=self.title, description=f'Description: {self.description}')
        
        if self.agrees != []:
            str_agrees = [self.bot.get_user(person).mention for person in self.agrees]
            agrees_value = '\n'.join(str_agrees)
        else:
            agrees_value = 'Noone so far'
        embed.add_field(name='Can attend:', value=agrees_value)
        
        if self.disagrees != []:
            str_disagrees = [self.bot.get_user(person).mention for person in self.disagrees]
            disagrees_value = '\n'.join(str_disagrees)
        else:
            disagrees_value = 'Noone so far'
        embed.add_field(name='Can\'t attend:', value=disagrees_value)

        return embed

    # Methods for later usage
    def add_agree(self, user_id):
        self.agrees.append(user_id)

    def remove_agree(self, user_id):
        self.agrees.remove(user_id)

    def add_disagree(self, user_id):
        self.disagrees.append(user_id)

    def remove_disagree(self, user_id):
        self.disagrees.remove(user_id)

    # Recreates embed and edits the message
    async def reload_embed(self):
        embed = self.create_embed()
        await self.message.edit(embed=embed)

    async def send_initial_message(self, ctx, channel):
        embed = self.create_embed()
        return await channel.send(embed=embed)

    @menus.button('\N{THUMBS UP SIGN}')
    async def on_thumbs_up(self, payload):
        if payload.user_id not in self.agrees:         
            self.add_agree(payload.user_id)
            if payload.user_id in self.disagrees:
                self.remove_disagree(payload.user_id)
            await self.reload_embed()

    @menus.button('\N{THUMBS DOWN SIGN}')
    async def on_thumbs_down(self, payload):
        if payload.user_id not in self.disagrees:
            self.add_disagree(payload.user_id)
            if payload.user_id in self.agrees:
                self.remove_agree(payload.user_id)
            await self.reload_embed()

    @menus.button('\N{CROSS MARK}')
    async def on_clear(self, payload):
        if payload.user_id in self.agrees:
            self.remove_agree(payload.user_id)
        elif payload.user_id in self.disagrees:
            self.remove_disagree(payload.user_id)
        await self.reload_embed()

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        if payload.user_id == self.bot.real_owner_id:
            self.stop()

# Load config
class Config:
    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).parent.absolute()/'config.json'
        self.path = path
        self.load()

    def load(self):
        # Tries to load config file
        try:
            with open(self.path, 'r') as file:
                config = json.load(file)
        # If it fails it will print error and end itself.
        except FileNotFoundError as e:
            print(f"Config file not found!\n{e}")
            sleep(2)
            print("Exiting...")
            sleep(7)
            quit()
        try:
            self.token = config['token']
            if self.token == "":
                print("No token found!")
                sleep(2)
                print("Exiting...")
                sleep(7)
                quit()
            self.prefix = config['prefix']
            if self.prefix == "":
                self.prefix = 'o!'
            self.time = config['time']
            self.channel_id = config['channel_id']
            if self.channel_id == "":
                print("No channel ID found!")
                sleep(2)
                print("Exiting...")
                sleep(7)
                quit()
            self.title = config['title']
            if self.title == "":
                self.title = 'Generic title.'
            self.description = config['description']
            if self.description == "":
                self.description = 'No description given.'
        except KeyError as e:
            print(f"{e} is missing in config!")
            sleep(2)
            print("Exiting...")
            sleep(7)
            quit()

# Custom bot class
class CBot(commands.Bot):
    def __init__(self):
        # Load config
        self.config = Config()

        # Logging | Logs discords internal stuff
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
        self.handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(self.handler)

        # Event variable
        self.custom_event = None

        super().__init__(
        command_prefix=self.config.prefix,
        help_command=None,
        description='Discord bot that sends message at specific time which users can react to.')

        self.loop.create_task(self.setup_func())

    async def setup_func(self):
        await self.wait_until_ready()

        hour = self.config.time['hour']
        minute = self.config.time['minute']
        second = self.config.time['second']
        config_time = hour*3600 + minute*60 + second

        # Gets amount of seconds since midnight
        now = datetime.now()
        actual_time = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        # It's next day
        if config_time < actual_time:
            # 1 day is 86 400 seconds
            sleep_time = (86400 - actual_time) + config_time

        # It's now
        elif config_time == actual_time:
            sleep_time = 0

        # It's today
        elif config_time > actual_time:
            sleep_time = config_time - actual_time
        
        # Wait until the set time
        await asleep(sleep_time)

        # Start message loop
        embed_message.start()

bot = CBot()

# Event is called when the bots internals are ready to handle commands, etc.
@bot.event
async def on_ready():
    print('Bot is ready.')
    print(f'Logged in as {bot.user}')

@commands.is_owner()
@bot.command()
async def event(ctx):
    bot.event = Event(title=bot.config.title, description=bot.config.description)
    await bot.event.start(ctx)

@tasks.loop(hours=24)
async def embed_message():
    bot.event = Event(title=bot.config.title, description=bot.config.description)
    channel = bot.get_channel(bot.config.channel_id)
    message = await channel.send(content='Creating event...', delete_after=2)
    ctx = await bot.get_context(message)
    await bot.event.start(ctx)

# Runs the bot (any code after this point won't be executed)
bot.run(bot.config.token)
import discord
import os
import asyncio
import socket
from global_data import (
    g_data,
    g_attributes,
    g_diff)
import numpy as np

TOKEN = os.getenv("D_TOKEN")
intents = discord.Intents.all()


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player_dict = {}
        self.channels = []
        self.rdy = False
        self.test_id = 0
        self.attr = [[str(i), a[:3], a] for i, a in enumerate(g_attributes)]
        self.p_bonus = {}
        # self.setup_dash_com()

    def setup_dash_com(self):
        self.HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        self.PORT = 65000        # Port to listen on (non-privileged ports are > 1023)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.HOST, self.PORT))
        s.listen()
        self.conn, addr = s.accept()
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.bg_server())

    async def on_ready(self,):
        self.guild = client.guilds[0]
        print(f"{client.user} is connected to the following guild:\n" + f"{self.guild.name}(id: {self.guild.id})")
        print("Guild Members:\n - " + "\n - ".join([member.name+"/"+member.nick for member in self.guild.members]))
        self.private_c_overwrite = {self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                    self.guild.me: discord.PermissionOverwrite(read_messages=True)}
        self.mg = next((m for m in self.guild.members if m.nick == "aightech" or m.name == "alexis devillard"), None)
        for m in self.guild.members:
            await m.create_dm()
            self.p_bonus[m.nick] = {a: 0 for a in g_attributes}
        self.rdy = True

    async def on_message(self, message):
        if message.author == client.user:
            return
        mess = message.content
        data = mess.split(" ")
        if mess.startswith('-'):

            # INFO
            if mess[1:].startswith('i') or mess[1:].startswith('info'):
                await message.channel.send("Information:\n# Attributes:\n" +  # Liste available attributes
                                           "\n\t\t".join(str(i) + "\t" + a[:3] + "\t" + a + "\n" for i, a in enumerate(g_attributes)))

            # TEST
            if mess[1:].startswith('t') or mess[1:].startswith('test'):
                attribute = next((l_a[2] for l_a in self.attr if data[1] in l_a), -1)  # Interprete the attribute to test
                if attribute == -1:
                    await message.channel.send("Error: " + message)
                    return
                self.test_id += 1
                if message.author == self.mg:  # Test comming from the GM: no fomat error
                    diff, name = data[2], data[3]
                else:
                    await message.channel.send("[#" + str(self.test_id) + "]\t\t**" + message.author.nick + "** \t**" + attribute +
                                               '**\t  :control_knobs::question:')

                    def check(msg):
                        return msg.channel == message.channel and msg.content.startswith('#'+str(self.test_id)) and msg.author == self.mg
                    msg = await client.wait_for("message", check=check)  # Wait for the MG diff
                    diff, name = msg.content.split(" ")[1], message.author.nick

                str_result, result = self.roll(attribute, diff, name)  # Roll the dice
                await message.channel.send("[#" + str(self.test_id) + "]\t\t**" + message.author.nick + "** \t**" + attribute + '**\t*' + diff +
                                           "*\t :control_knobs:" + result)
                await message.author.dm_channel.send("**" + attribute + '**\t*' + diff + "*\t :control_knobs:" + str_result + result)

    def roll(self, attribute, diff, name):
        x = g_data[name]["attribute"][attribute] + self.p_bonus[name][attribute]
        a = g_diff[diff]['a']
        b = g_diff[diff]['b']
        target = a*x + b
        dice = np.random.randint(0, 100)
        if target >= dice:
            str_result = "["+str(dice) + "<" + str(target) + "] "
            result = ":white_check_mark: (success)"
        else:
            str_result = "["+str(dice) + ">" + str(target) + "] "
            result = ":x: (fail)"
        return str_result, result

    async def bg_server(self):
        await self.wait_until_ready()
        while True:
            data = self.conn.recv(50)
            if data and self.rdy:
                data = str(data)[2:].split(":")

                # Setting player name to an index
                if data[0] == 'S':
                    print(data[1] + ":" + data[2])
                    self.player_dict[data[1]] = data[2]  # num:pseudo

                # New channel
                if data[0] == 'C':
                    num_c = int(data[1])
                    for c in self.guild.channels:
                        if c.name == "channel n"+str(num_c):
                            return
                    await self.guild.create_voice_channel("channel n" + str(num_c), overwrites=self.private_c_overwrite)

                # Move player in channel
                if data[0] == 'M':
                    p_nick, num_c = self.player_dict[data[1]], int(data[2])
                    player = next((p for p in self.guild.members if p.nick == p_nick), None)  # find player
                    channel = next((c for c in self.guild.channels if c.name == "channel n"+str(num_c)), None)  # find channel
                    if channel is not None and player is not None:  # move player
                        await player.move_to(channel)

                # Add bonus
                if data[0] == "B":
                    p_nick = self.player_dict[data[1]]
                    if data[2] == "c":  # Clear bonus
                        self.p_bonus[p_nick] = {a: 0 for a in g_attributes}
                    else:
                        self.p_bonus[p_nick][data[2]] += int(data[3])
            await asyncio.sleep(1)


client = MyClient(intents=intents)
client.run(TOKEN)

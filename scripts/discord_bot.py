import discord
import os
import asyncio
import socket

TOKEN = os.getenv("D_TOKEN")
intents = discord.Intents.all()


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 65000        # Port to listen on (non-privileged ports are > 1023)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        self.conn, addr = s.accept()
        self.player_dict = {}
        self.channels = []
        self.rdy = False

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.bg_server())

    async def on_ready(self,):
        print("Discord bot logged in as: %s, %s" % (client.user.name, client.user.id))
        for guild in client.guilds:
            print(f"{client.user} is connected to the following guild:\n"
                  f"{guild.name}(id: {guild.id})")
            members = "\n - ".join([member.name+"/"+member.nick for member in guild.members])
            print(f"Guild Members:\n - {members}")
            self.guild = guild
            print(self.guild)
            self.rdy = True

    async def bg_server(self):
        await self.wait_until_ready()
        while True:
            data = self.conn.recv(50)
            if data and self.rdy:
                data = str(data)[2:].split(":")
                if data[0] == 'S':  # Setting
                    print(data[1] + ":" + data[2])
                    self.player_dict[data[1]] = data[2]  # num:pseudo
                if data[0] == 'C':  # New channel
                    num_c = int(data[1])
                    print("create channel " + str(num_c))
                    exist = False
                    for c in self.guild.channels:
                        if c.name == "channel n"+str(num_c):
                            exist = True
                            break
                    if not exist:
                        overwrites = {
                            self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            self.guild.me: discord.PermissionOverwrite(read_messages=True)
                        }
                        await self.guild.create_voice_channel("channel n" + str(num_c), overwrites=overwrites)
                if data[0] == 'M':  # Move player in channel
                    p_nick = self.player_dict[data[1]]
                    num_c = int(data[2])

                    # find player
                    player = None
                    for p in self.guild.members:
                        if p.nick == p_nick:
                            player = p
                            break

                    # find channel
                    channel = None
                    for c in self.guild.channels:
                        if c.name == "channel n"+str(num_c):
                            channel = c

                    # move player
                    if channel is not None and player is not None:
                        print(p_nick + " moved to " + channel.name)
                        await player.move_to(channel)

                if data[0] == "D":  # Delete channel
                    num_c = int(data[1])
                    for c in self.guild.channels:
                        if c.name == "channel n"+str(num_c):
                            print("deleted channel " + str(num_c))
                            await c.delete()
                            break
            await asyncio.sleep(1)


client = MyClient(intents=intents)
client.run(TOKEN)

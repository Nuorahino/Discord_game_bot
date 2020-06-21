import discord
from discord.ext import commands
import asyncio
import os

class Meme(commands.Cog):

    def __init__(self, client):
        self.client = client
        print('Meme loaded')

    @commands.Cog.listener()
    #@commands.check(lambda member, before,after: after.channel != None and befor.channel == None and member.id == 237254419769458688)
    async def on_voice_state_update(self,member,before,after):
        if after.channel != None and before.channel == None and member.id == 693172719507734604:
            print("Voice Channel joined")
            vc = await after.channel.connect()
            vc.play(discord.FFmpegPCMAudio('cogs/Meme/TRUMP SINGS happy birthday.mp3'))
            while vc.is_playing():
                await asyncio.sleep(100)
            await vc.disconnect()
            await member.edit(voice_channel=None)



def setup(client):
    client.add_cog(Meme(client))

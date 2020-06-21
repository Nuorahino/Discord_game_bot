import discord
import random
import os           # To remove files and maybe something else
from discord.ext import commands
import asyncio
from PIL import Image          #for image processing and conversion
import requests     #download Discord Avatars

client = commands.Bot(command_prefix = '/')


#####################################################
#Troll Stuff
#####################################################

#@client.event
##@commands.check(lambda member, before,after: return (after.channel != None and befor.channel == None and member.id == 237254419769458688))
#async def on_voice_state_update(member,before,after):
#    if before.channel != after.channel and before.channel != None and member.id == 237254419769458688:
#        print("Voice Channel joined")
#        await before.channel.disconnect()

#####################################################
#Actual Stuff
#####################################################

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.idle, activity=discord.Game('waiting'))
    print("Bot is ready")
    client.load_extension(f'cogs.Meme')


def bot_member(ctx):
    for x in client.get_all_members():
        if x.id == 714561396851081257:
            member = x
    return(member)

def is_bot_activity(ctx, activity):
    return(bot_member(ctx).activity == activity)


def if_bot_is_idle(ctx):
    return(bot_member(ctx).status == discord.Status.idle)

@client.command(brief='loads the Secret Hitler Cog')
@commands.check(if_bot_is_idle)
async def play_SH(ctx):
    client.load_extension(f'cogs.SH')
    await client.change_presence(status = discord.Status.idle, activity=discord.Activity(name = 'Secret Hitler, waiting for players', type = discord.ActivityType.watching))
    await ctx.send('Loading Secret Hitler Plugin')
    #server = client.get_guild(714560653930528858)
    #role = 715130393191252019
    #await bot_member(ctx).add_roles(role)
    #await ctx.add_roles(bot_member(ctx), discord.utils.get(member.server.roles, name='Secret Hitler Player'))

@client.command(brief="Loads an extension which isn't SH")
async def load(ctx, extension):
    if extention == SH:
        return
    client.load_extension(f'cogs.{extension}')

@client.command(brief="Unloads an extension which isn't SH")
async def unload(ctx, extension):
    if extention == SH:
        return
    client.unload_extension(f'cogs.{extension}')


@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

@client.command(brief='removes the last 20 messages')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount = 20):
    await ctx.channel.purge(limit=amount)

#@client.command()
#async def
#member_name, member_discriminator = member.split('#')


client.run('NzE0NTYxMzk2ODUxMDgxMjU3.XswdWg.NNBUtyx8FBue3RsoCYOHextl-2U')

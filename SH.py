import discord
from discord.ext import commands
import random
import asyncio
import os           # To remove files and maybe something else
from PIL import Image          #for image processing and conversion
from PIL import ImageOps        #for inverted images
import requests     #download Discord Avatars
#import SH_gameclass

#pics_used = ['std','png']
pics_used = ['HD','jpg']
bot_id = 714561396851081257
voice_channel = 720281873825398784
sound_lib = ['Meinen_neuen_Lederlappen.mp3','menschlicher_Lappen1.mp3','menschlicher_Lappen2.mp3','direkt_20_Stueck_geholt.mp3']
sound_fas = ['Schlurp1.mp3','Schlurp2.mp3','Schlurp3.mp3','Schlurp4.mp3','Schlurp6.mp3','Schlurp7.mp3']
sound_lib_victory = ['UDSSR_shittyflute.mp3']
sound_hitler_dead = ['Der_zweite_Weltkrieg_macht_keinen_Spass_mehr.mp3']
sound_fas_victory = ['Id_like_to_sign_this_bill.mp3','How_is_that_a_victory.mp3']
sound_hitler_elected = ['Ich_kapituliere_nicht.mp3']
sound_crazy_dude = ['Crazydude2_low.mp3','Crazydude2.mp3','Crazydude.mp3']


def rescale_height(im1,im2):
    im2 = im2.resize((int(float(im2.size[0])*float(im1.size[1]/float(im2.size[1]))) ,im1.size[1]))
    return im2

def rescale_width(im1,im2):
    im2 = im2.resize((im1.size[0],int(float(im2.size[1])*float(im1.size[0]/float(im2.size[0])))))
    return im2

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


class SH(commands.Cog):
    #Class which contains the actuall game
    class SH_game:


        def __init__(self, players):
            presidential_powers = [['None','None','Examine','Kill','Kill','None'],['None','Identity','President','Kill','Kill','None'],['Identity','Identity','President','Kill','Kill','None']]
            fs_nr = 1 + int((len(players)-5)/2)
            lib_nr = 3 + int((len(players)-4)/2)
            roles = ['hitler'] + ['fascist']*fs_nr + ['liberal']*lib_nr
            random.shuffle(players)
            random.shuffle(roles)
            self._players = dict(zip(players, roles))
            random.shuffle(players)
            self._player_order = list(players)
            self._next_presidents = players
            self._presidential_powers = presidential_powers[fs_nr -1]


            #ingame variables
            self._passed_policies = [0,0]
            #self._passed_policies = [0,0]
            self._draw_pile = ['fascist']*11 + ['liberal']*6
            random.shuffle(self._draw_pile)
            self._discard_pile = list()
            self._rejected_governments = 0
            self._nominated_chancellor = None
            self._last_government = [None]*2
            self._investigated = list()

        def return_party(self,player):
            if self._players[player] == 'liberal':
                return 'liberal'
            else:
                return 'fascist'

        def return_president(self):
            return self._next_presidents[0]

        def return_chancellor(self):
            return self._nominated_chancellor

        def return_players(self):
            return self._players.keys()

        def return_presidential_power(self):
            return self._presidential_powers[self._passed_policies[1]-1]

        def return_investigate_candidates(self):
            res = list()
            for x in self._players.keys():
                if x in self._investigated:
                    continue
                if is_president(x):
                    continue
                res.append(x)
            return res

        def return_other_players(self):
            res = list()
            for x in self._players.keys():
                if x != self._next_presidents[0]:
                    res.append(x)
            return res

        def investigate(self,player):
            self._investigated.append(player)
            return self.return_party(player)


        def is_hitler(self,player):
            if self._players[player] == 'hitler':
                return True
            else:
                return False


        def return_chancellor_candidates(self):
            res = list(self._players.keys())
            res.remove(self._next_presidents[0])
            if self._last_government[1] == None:
                return res
            else:
                if self._last_government[1] != self._next_presidents[0]:
                    try:
                        res.remove(self._last_government[1])
                    except:
                        pass
                if(len(self._players.keys()) > 5):
                    try:
                        res.remove(self._last_government[0])
                    except:
                        pass
            return res


        def list_next_presidents(self):
           return self._next_presidents


        def is_president(self, player):
            if self._next_presidents[0] == player:
                return True
            else:
                return False

        def is_chancellor(self, player):
            if self._nominated_chancellor == player:
                return True
            else:
                return False

        def is_fascist(self,player):
            if self._players[player] == 'fascist':
                return True
            else:
                return False


        def was_not_in_last_government(self,player):
            return player in self._last_government


        def reshuffle_deck(self):
            self._draw_pile += self._discard_pile
            random.shuffle(self._draw_pile)
            self._discard_pile = list()

        #return all fascists and hitler
        def show_fascists(self):
            res = [list(),list()]
            for x in self._players.keys():
                if (self._players[x] == 'fascist'):
                    res[0].append(x)
            for x in self._players.keys():
                if (self._players[x] == 'hitler'):
                    res[1].append(x)
            return res


        def nominate_chancellor(self,player):
            self._nominated_chancellor = player


        def discard_card(self,card):
            self._discard_pile.append(card)


        def fascist_policy_victory(self):
            if self._passed_policies[1] >= 6:
                return True
            else:
                return False


        def liberal_policy_victory(self):
            if self._passed_policies[0] >= 5:
                return True
            else:
                return False


        def pass_policy(self,policy):
            if (policy == 'fascist'):
                self._passed_policies[1] += 1
            elif (policy == 'liberal'):
                self._passed_policies[0] += 1


        #Insert the vote as a list
        def enter_vote(self, vote):
            hitler_won = False
            if(sum(vote) > len(self._players)/2):
                if self.is_hitler(self._nominated_chancellor) and self._passed_policies[1] >= 3:
                   hitler_won = True
                self.make_chancellor()
                return(True, hitler_won,False)
            else:
                policy_auto_passed = self.reject_chancellor()
                return(False,False,policy_auto_passed)


        #make a new player chancellor
        def make_chancellor(self):
            self._rejected_governments = 0
            self._last_government[0] = self.return_president()
            self._last_government[1] = self.return_chancellor()


        def change_government(self):
            self._nominated_chancellor = None
            last = self._next_presidents[0]
            self._next_presidents.remove(last)
            if not last in self._next_presidents: # Bc of Presidential Power
                self._next_presidents.append(last)


        #make a new player chancellor
        def reject_chancellor(self):
            self.change_government()
            self._rejected_governments += 1
            if (self._rejected_governments >= 3):
                self._rejected_governments = 0
                if(len(self._draw_pile) < 3):
                    self.reshuffle_deck()
                x = self._draw_pile.pop(0)
                self.pass_policy(x)
                return True
            return False


        #draw policies and return the policies and the president
        def draw_policies(self):
            if(len(self._draw_pile) < 3):
                self.reshuffle_deck()
            drawn_policies = [self._draw_pile.pop(0),self._draw_pile.pop(0),self._draw_pile.pop(0)]

            return (drawn_policies)


        def choose_president(self, player):
            self._next_presidents.insert(1,player)


        def examine_policies(self):
            if(len(self._draw_pile) < 3):
                self.reshuffle_deck()
            drawn_policies = [self._draw_pile[0],self._draw_pile[1],self._draw_pile[2]]

            return (drawn_policies)


        def kill(self,player):
            hitler_lost = self.is_hitler(player)
            self._players.pop(player)
            self._next_presidents.remove(player)
            return hitler_lost


        def return_safe_data(self):
            return(self._player_order, self._players, self._next_presidents, self._passed_policies, self._draw_pile, self._discard_pile, self._last_government, self._rejected_governments, self._investigated)


        def recover_game(self, player_order, players, next_presidents, passed_policies, draw_pile, discard_pile, last_government, rejected_governments, investigated):
            self._player_order = player_order
            self._players = players
            self._next_presidents = next_presidents
            self._passed_policies = passed_policies
            self._draw_pile = draw_pile
            self._discard_pile = discard_pile
            self._last_government = last_government
            self._rejected_governments = rejected_governments
            self._investigated = investigated
            presidential_powers = [['None','None','Examine','Kill','Kill','None'],['None','Identity','President','Kill','Kill','None'],['Identity','Identity','President','Kill','Kill','None']]
            self._presidential_powers = presidential_powers[len(player_order) -1]

#############################################################################################################
# Start of Discord Commands                                                                                 #
#############################################################################################################

    def __init__(self, client):
        '''
        Initializes the Discord Bot, with it's commands, but without an actual game object.
        This function should exclusively be called, when the cog is loaded.
        '''
        self.client = client
        self._lobby = None
        self._ballets = [None]
        print('SH Cog loaded')
        self._channel = self.client.get_channel(714576804899323984)
        self._voice_channel = self.client.get_channel(voice_channel)
        #global SH_player                # Currently makes this a global variable, it works, but is ugly
        #SH_player = self._players

    @commands.Cog.listener()
    async def on_ready(self):
        print('SH is ready')

#############################################################
#Checks to see if a player is allowed to execute commands   #
#############################################################



    @commands.command(brief='Opns a new SH Game', description = 'Opens a new Secret Hitler game by sending a message in the Secret Hitler chat, which players can join by hitting the like button')
    async def open_SH(self,ctx):
        '''
        Send a Message into the designated SH channel, when players add a like to the post, they join the lobby.
        For Multi Game Access, this has to work with multiple Channels.
        '''
        if (self._lobby == None):
            self._players = list()
            self._status = 'Waiting for Players'
            self._lobby = await self._channel.send('Waiting for players to join Secret Hitler')
            await self._lobby.add_reaction( '👍')
        else:
            await ctx.send('Already a Lobby running')


    def is_player(self, player):
        '''
        Returns if the player is currently in a SH Game.
        '''
        if(player in self._players):
            return True
        else:
            return False


    #Invert the result of a check for discord.py
    def inverse_check(f):
        '''
        This function inverses a predicate (check) for the discord.py commands, might work for any function returning a bool
        '''
        def predicate(ctx):
            return (not bool(f(ctx)))
        return commands.check(predicate)


    def check_if_it_is_bot(self, user):
        '''
        Detecs if a user is the bot itself.
        This function is mainly called for checking whether a reaction is from the bot itself
        '''
        return user.id != bot_id


#    #Check if the bot is doing a certain activity
#    def is_bot_activity(activity):
#        global bot_member
#        def predicate(ctx):
#            return bot_member.activity == activity
#        return commands.check(predicate)

#############################################################
#Admin and pregame Commands                                 #
#############################################################

    async def remove_reaction(reaction,user):
        await reaction.remove(user)


    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        '''
        This function detects reactions, it filters out the reactions from the bot.
        '''
        if not self.check_if_it_is_bot(user):
            return
        elif (reaction.message.id == self._lobby.id):
            if (len(self._players) >= 10):
                await self._channel.send(f'The Game is already full')
            elif not self.is_player(user):
                #await self._channel.send(f'{user.name} has joined the lobby for Secret Hitler')
                self._players.append(user)                       # Add the Player to the list
                #await reaction.remove(user)
        elif (reaction.message.id in self._ballets and self._vote[user] == None):
            game_obj = self._SH_game
            if reaction.emoji ==  '👍':
                self._vote[user] = True
                if (self.check_votes_missing(game_obj) == 0):
                    await self.cast_votes(game_obj)
            elif reaction.emoji ==  '👎':
                self._vote[user] = False
                if (self.check_votes_missing(game_obj) == 0):
                    await self.cast_votes(game_obj)


    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction,user):
        '''
        The Bot checks if there is a reaction is removed, and he can react accordingly
        '''
        if self.check_if_it_is_bot(user):
            return
        if (reaction.message.id == self._lobby.id):
            if  self.is_player(user):
                #await self._channel.send(f'{user} left the lobby for Secret Hitler')
                self._players.remove(user)                       # Remove the Player to the list
        elif (reaction.message.id in self._ballets and self._vote[user] != None):
            if reaction.emoji ==  '👍' and self._vote[user] == True:
                self._vote[user] = None
            elif reaction.emoji ==  '👎' and self._vote[user] == False:
                self._vote[user] = None



    @commands.command(brief='Return the status of the current SH game', description="Sends the status of the currently active Secret Hitler game into this chat. \n if the game is awaiting player votes, it will say, which player haven't voted yet")
    async def status_SH(self,ctx):
        await ctx.send(self._status)
        if (self._status ==  'Waiting for players to cast their vote'):
            res = 'Waiting on '
            for x in self._players:
                if(self._vote[x] == None):
                    res = res + x.name
            res +=  ' to cast their votes'
            await ctx.send(res)


    def check_vote(self,reaction,user,player,message):
        return user == player and reaction.message.id == message and (reaction.emoji =='👍' or reaction.emoji == '👎')


    @commands.command(brief='Starts the game with the current players', description = 'It starts an instance of Secret Hitler, with all players which upvoted the game post. \n The bot will then remove the post, and starts the game. \n It will send the roles out in privat, randomly selects a player order.')
    #@commands.check(Salo_has_Birthday)
    @commands.has_any_role('Game_master')
    async def start_SH(self, ctx):
        if (self._status !=  'Waiting for Players' or self._lobby == None):
            await ctx.send(f'There is no game to start')
        elif (len(self._players) < 5):
            await ctx.send(f'The Game needs at least {5 - len(self._players)} more Players to start')
        else:
            print("Voice Channel joined")
            self._vc = await self._voice_channel.connect()
            self._last_player = None
            await self._lobby.delete()
            await self.client.change_presence(status = discord.Status.online, activity=discord.Game('Secret Hitler'))
            await self._channel.send('Secret Hitler is starting')
            self._SH_game = self.SH_game(self._players)
            for x in self._players:                                      #Sending the fascist Info out
                if self._SH_game.is_fascist(x):
                    await self.SH_send_fascists(x,self._SH_game)
                if (len(self._players) < 7):
                    if self._SH_game.is_hitler(x):
                        await self.SH_send_fascists(x,self._SH_game)        #Hitler gets fascist Info
            for x in self._players:                                     # Send out player roles
                await x.send(file = discord.File(f'cogs/picture/{pics_used[0]}/{self._SH_game._players[x]}_Role.{pics_used[1]}'))
                await x.send(f'Your role is: {self._SH_game._players[x]}')
            #Load the player Avatars
            with requests.get(self._SH_game._player_order[0].avatar_url) as r:
                img_data = r.content
            with open('SH/image_name.webp', 'wb') as handler:
                handler.write(img_data)
            self._player_avatar = Image.open("SH/image_name.webp").convert("RGB")
            for x in self._SH_game._player_order[1:]:
                with requests.get(x.avatar_url) as r:
                    img_data = r.content
                with open('SH/image_name.webp', 'wb') as handler:
                    handler.write(img_data)
                im = Image.open("SH/image_name.webp").convert("RGB")
                self._player_avatar = get_concat_h(self._player_avatar, im.resize((self._player_avatar.size[1],self._player_avatar.size[1])))
            os.remove('SH/image_name.webp')
            await self.SH_draw_board(self._SH_game)
            await self.SH_next_round(sefl._SH_game)


    #End this game instanz
    async def end_game_SH(self,game_obj):
        await self.client.change_presence(status = discord.Status.idle, activity=discord.Activity(name = 'Secret Hitler, waiting for players', type = discord.ActivityType.watching))
        await self._channel.send('Secret Hitler Game ended')
        self._lobby = None      # Remove the lobby
        self._SH_game = None
        try:
            await self._vc.disconnect()
            os.remove('SH/order.jpeg')
        except:
            print('game canceled')

    #Unloads and disables all SH commands
    @commands.command(brief='Unloads the SH cog', description='Stops the current game of Secret Hitler, and unloads its cog')
    @commands.has_any_role('Game_master')
    async def unload_SH(self, ctx):
        await self.end_game_SH(self._SH_game)
        await self.client.change_presence(status = discord.Status.idle, activity=discord.Game('waiting'))
        await ctx.send('Secret Hitler Plugin unloaded')
        print('SH Unloaded')
        self.client.unload_extension(f'cogs.SH')

#############################################################
# Ingame Commands: Should later only be enabled for players #
#############################################################

    async def SH_pick_player(self, eligiable_candidates, message, remove = True):
        candidates = [None] * len(eligiable_candidates)
        candidates_id = [None] * len(eligiable_candidates)
        for i in range (len(eligiable_candidates)):
            candidates[i] = await self._channel.send(message.format(player = eligiable_candidates[i]))
            await candidates[i].add_reaction('👍')
            candidates_id[i] = candidates[i].id
        reaction, user = await self.client.wait_for('reaction_add',check=lambda reaction,user: self.president_pick_test(self._SH_game,reaction,user,candidates_id))
        pick = None
        for i in range (len(candidates_id)):
            if reaction.message.id == candidates_id[i]:
                pick = eligiable_candidates[i]
                if remove:
                    await candidates[i].delete()
            else:
                await candidates[i].delete()
        return pick


    #Made with VIM <3
    async def SH_draw_players(self, game_obj):
        res = Image.new('RGB', (0,0))
        for x in game_obj._player_order:
            if game_obj.is_president(x):
                img = Image.open(f'cogs/picture/{pics_used[0]}/president.jpg')
                if res.size[0] == 0:
                    res = img
                else:
                    res = get_concat_h(res, img)
            elif game_obj.is_chancellor(x):
                img = Image.open(f'cogs/picture/{pics_used[0]}/chancellor.jpg')
                if res.size[0] == 0:
                    res = img
                else:
                    res = get_concat_h(res, img)
            elif x == game_obj._last_government[0]:
                img = Image.open(f'cogs/picture/{pics_used[0]}/last_president.jpg')
                if res.size[0] == 0:
                    res = img
                else:
                    res = get_concat_h(res, img)
            elif x == game_obj._last_government[1]:
                img = Image.open(f'cogs/picture/{pics_used[0]}/last_chancellor.jpg')
                if res.size[0] == 0:
                    res = img
                else:
                    res = get_concat_h(res, img)
            else:
                img = Image.open(f'cogs/picture/{pics_used[0]}/empty.jpg')
                if res.size[0] == 0:
                    res = img
                else:
                    res = get_concat_h(res, img)
        self._positions = rescale_height(Image.new('RGB',(0,50)), res)
        res = get_concat_v(self._positions, rescale_width(self._positions, self._player_avatar))
        res.save('SH/player_state.jpeg')
        self._last_player = await self._channel.send(file = discord.File('SH/player_state.jpeg'))
        os.remove('SH/player_state.jpeg')


    async def SH_draw_board(self,game_obj):
        lib_passed = game_obj._passed_policies[0]
        fas_passed = game_obj._passed_policies[1]
        gov_rej = game_obj._rejected_governments
        im_board_lib = Image.open(f'cogs/picture/{pics_used[0]}/{gov_rej+1}Liberal_board{lib_passed}.{pics_used[1]}')
        im_board_fas = Image.open(f'cogs/picture/{pics_used[0]}/{len(game_obj._player_order)}fascist_board{fas_passed}.{pics_used[1]}').resize(im_board_lib.size)
        im_draw = Image.open(f'cogs/picture/{pics_used[0]}/Policy{len(game_obj._draw_pile)}.{pics_used[1]}')
        im_discard = Image.open(f'cogs/picture/{pics_used[0]}/Policy{len(game_obj._discard_pile)}.{pics_used[1]}')
        im_draw = rescale_height(im_board_lib, im_draw)
        im_discard = rescale_height(im_board_lib, ImageOps.invert(im_discard))
        res_board = get_concat_v(get_concat_h(im_board_lib,im_draw),get_concat_h(im_board_fas,im_discard))
        res_board.save('SH/board_state.jpeg')
        await self._channel.send(file = discord.File('SH/board_state.jpeg'))
        os.remove('SH/board_state.jpeg')
        await self.SH_draw_players(game_obj)

        if game_obj.fascist_policy_victory():
            self._vc.play(discord.FFmpegPCMAudio(f'cogs/Meme/{random.choice(sound_fas_victory)}'))
            while self._vc.is_playing():
                await asyncio.sleep(10)
            await self._channel.send('Fascists won through signing fascist laws')
            await self.end_game_SH(game_obj)
        elif game_obj.liberal_policy_victory():
            self._vc.play(discord.FFmpegPCMAudio(f'cogs/Meme/{random.choice(sound_lib_victory)}'))
            while self._vc.is_playing():
                await asyncio.sleep(10)
            await self._channel.send('Liberals won through signing liberal laws')
            await self.end_game_SH(game_obj)


    async def SH_next_round(self,game_obj):
        self.write_safe_file()
        if self._last_player != None:
            await self._last_player.delete()
        await self.SH_draw_players(game_obj)
        self._status = 'Waiting for a chancelor to be announced'
        await self.SH_make_chancellor(game_obj)
        chancellor =  game_obj.return_chancellor()
        self._vote = dict(zip(game_obj.return_players(), [None]*len(game_obj.return_players())))
        await self._last_player.delete()
        await self.SH_draw_players(game_obj)
        self._status = 'Waiting for players to cast their vote'
        await self.SH_start_vote(game_obj.return_president().name,chancellor.name)

    async def Legeslative_action(self, game_obj):
        policies = await self.SH_draw_policies(game_obj)
        president = game_obj.return_president()
        chancellor = game_obj.return_chancellor()
        policies = await self.SH_president_select_policies(game_obj,president,policies)
        self._status = 'Policies are being passed on to the chancellor'
        policy = await self.SH_chancellor_select_policies(game_obj,president, chancellor, policies)
        await self.SH_draw_board(game_obj)
        if policy == 'fascist':
            self._vc.play(discord.FFmpegPCMAudio(f'cogs/Meme/{random.choice(sound_fas)}'))
            if game_obj._passed_policies[0] == 3 and game_obj._passed_policies[1]:
                self._vc.play(discord.FFmpegPCMAudio('cogs/Meme/{random.choice(sound_crazy_dude)}'))
            lib_won = await self.SH_presidential_power(game_obj)
            if lib_won:
                await self.end_game_SH(game_obj)
                return
        if policy == 'liberal':
            self._vc.play(discord.FFmpegPCMAudio(f'cogs/Meme/{random.choice(sound_lib)}'))

        game_obj.change_government()
        await self.SH_next_round(game_obj)

    @commands.command(brief='Shows the other fascists', description='This command only works when you are fascist in the active game.\n It sends the player names of the other fascists to the author in privat.')
    async def SH_show_fascists(self,ctx):
        if( self._SH_game.is_fascist(ctx.author)):
            SH_send_fascists(self,ctx.author, self._SH_game)
        else:
            await player.send('Damn you cheeky liberals')


    async def SH_send_fascists(self, player, game_obj):
            fascists = game_obj.show_fascists()
            res = 'Fasicsts are: '
            for x in fascists[0]:
                res += x.name
            res += '\nHitler: '
            res += fascists[1][0].name
            await player.send(res)


    @commands.command(brief='lists the next presidents', description='Returns a string with the order of next presidents. \n This string is send into the chat, in which the command is executed.')
    async def SH_next_presidents(self,ctx):
        res = 'The next presidents are: '
        for x in self._SH_game.list_next_presidents():
            res += str(x.name) + ', '
        await ctx.send(res)


    def president_pick_test(self, game_obj reaction, user, candidates):
        return game_obj.is_president(user) and reaction.message.id in candidates and reaction.emoji =='👍'

    async def SH_make_chancellor(self, game_obj):
        chancellor = await self.SH_pick_player(game_obj.return_chancellor_candidates(), "Nominate **{player.name}** as the next chancellor")
        game_obj.nominate_chancellor(chancellor)


    async def SH_start_vote(self, president, chancellor):
        self._ballets = [None] * len(self._players)
        for i in range (len(self._players)):
            self._ballets[i] = await self._players[i].send(f'Please enter your Vote for this Government: \nPresident: **{president}**\nChancellor: **{chancellor}**')
            await self._ballets[i].add_reaction('👍')
            await self._ballets[i].add_reaction('👎')
            self._ballets[i] = self._ballets[i].id


    def check_votes_missing(self, game_obj):
        count = 0
        for x in game_obj._players.keys():
            if self._vote[x] == None:
                count += 1
        return count

    async def cast_votes(self, game_obj):
        self._ballets = [None]
        await self._last_player.delete()

        voted = self._player_avatar.copy()
        yes = Image.open(f'cogs/picture/{pics_used[0]}/yes.png')
        yes.convert('RGBA')
        no = Image.open(f'cogs/picture/{pics_used[0]}/no.png')
        no.convert('RGBA')
        height = voted.size[1]
        yes = rescale_height(self._player_avatar,yes)
        no = rescale_height(self._player_avatar,no)
        for x in game_obj._players.keys():
            if self._vote[x] == True:
                voted.paste(yes, (game_obj._player_order.index(x)*height,0),yes)
            else:
                voted.paste(no, (game_obj._player_order.index(x)*height,0),no)
        voted.resize(self._player_avatar.size)
        res = get_concat_v(self._positions, rescale_width(self._positions, voted))
        res.save('SH/voted.jpeg')
        self._last_player = await self._channel.send(file = discord.File('SH/voted.jpeg'))
        os.remove('SH/voted.jpeg')

        president = game_obj.return_president()
        chancellor = game_obj.return_chancellor()
        passed, hitler_won, auto_passed = game_obj.enter_vote(self._vote.values())
        if (passed):
            if (hitler_won):
                await self._channel.send('You have elected Hitler as chancellor past 1933, the fascists have won')
                await self.end_game_SH(game_obj)
                return
            self._status = ' Passing policies'
            await self.Legeslative_action(game_obj)
        else:
            await self.SH_draw_board(game_obj)
            await self.SH_next_round(game_obj)


    async def SH_president_select_policies(self, game_obj, president, policies):
        policy_cards = list()
        for x in policies:
            if x == 'liberal':
                policy_cards.append(discord.File(f'cogs/picture/{pics_used[0]}/liberal.{pics_used[1]}'))
            elif x == 'fascist':
                policy_cards.append(discord.File(f'cogs/picture/{pics_used[0]}/fascist.{pics_used[1]}'))
        policy_message = [None]*3
        for i in range (len(policies)):
            policy_message[i] = await president.send(file=policy_cards[i])
            await policy_message[i].add_reaction('👍')
            await policy_message[i].add_reaction('👎')
        passed_policies = [None]*3
        while True:
            for i in range (3):
                reaction, user = await self.client.wait_for('reaction_add',check=lambda reaction,user: self.check_vote(reaction,user,president,policy_message[i].id))
                #await reaction.message.clear_reactions()
                #await president.send(reaction.emoji)
                if (reaction.emoji == '👍'):
                    passed_policies[i] = True
                elif (reaction.emoji == '👎'):
                    passed_policies[i] = False
            if(sum(passed_policies) == 2):
                break
            else:
                await president.send('Invalid vote, all votes have to be recasted')
        await president.send('Vote is correctly selected')
        for i in range (3):
            if passed_policies[i] == False:
                game_obj.discard_card(policies[i])
                policies.pop(i)
        return (policies)


    async def SH_chancellor_select_policies(self, game_obj, president,chancellor, policies):
        policy_cards = list()
        for x in policies:
            if x == 'liberal':
                policy_cards.append(discord.File(f'cogs/picture/{pics_used[0]}/liberal.{pics_used[1]}'))
            elif x == 'fascist':
                policy_cards.append(discord.File(f'cogs/picture/{pics_used[0]}/fascist.{pics_used[1]}'))

        policy_message = [None]*2
        for i in range (2):
            policy_message[i] = await chancellor.send(file=policy_cards[i])
            await policy_message[i].add_reaction('👍')
            await policy_message[i].add_reaction('👎')
        passed_policies = [None]*2
        if await self.SH_veto(game_obj,president,chancellor,policies):
            return
        while True:
            for i in range (2):
                reaction, user = await self.client.wait_for('reaction_add',check=lambda reaction,user: self.check_vote(reaction,user,chancellor,policy_message[i].id))
                #await reaction.message.clear_reactions()
                #await chancellor.send(reaction.emoji)
                if (reaction.emoji == '👍'):
                    passed_policies[i] = True
                elif (reaction.emoji == '👎'):
                    passed_policies[i] = False
            if(sum(passed_policies) == 1):
                break
            else:
                await chancellor.send('Invalid vote, all votes have to be recasted')
        await chancellor.send('Voted is correctly selected')
        res = None
        for i in range (2):
            if passed_policies[i] == False:
                game_obj.discard_card(policies[i])
            elif passed_policies[i] == True:
                res = policies[i]
                game_obj.pass_policy(policies[i])
        return res


    async def SH_draw_policies(self, game_obj):
        self._status = 'The policies are being send out to our president'
        return game_obj.draw_policies()


    async def SH_investigate(self,game_obj,president):
        member = await self.SH_pick_player(game_obj.return_other_players(), "Investigate **{player.name}**s party membership",False)
        await president.send(file = discord.File(f'cogs/picture/{pics_used[0]}/{game_obj.return_party(member)}_Party.{pics_used[1]}'))
        await president.send(f'**{member.name}** is **{game_obj.return_party(member)}**.')
        return member

    async def SH_make_next_president(self,game_obj):
        member = await self.SH_pick_player(game_obj.return_other_players(), "Make **{player.name}** the next President")
        res = None
        for x in self.client.get_all_members():
            if x.name == member.name and x.discriminator == member.discriminator:
                res = x
        game_obj.choose_president(res)
        return member


    async def SH_execution(self,game_obj):
        member = await self.SH_pick_player(game_obj.return_other_players(), "Kill **{player.name}**")
        img = Image.open(f'cogs/picture/{pics_used[0]}/skull.png')
        img = rescale_height(self._player_avatar, img)
        for i in range (len(game_obj._player_order)):
            if member == game_obj._player_order[i]:
                self._player_avatar.paste(img, (i*self._player_avatar.size[1],0),img)
        hitler_lost = game_obj.kill(member)
        return member, hitler_lost


    async def SH_presidential_power(self,game_obj):
        president = game_obj.return_president()
        if game_obj.return_presidential_power() == 'None':
            return False
        elif game_obj.return_presidential_power() == 'Examine':
            await self._channel.send('The President can inspect the next 3 policies')
            policies = game_obj.examine_policies()
            for x in policies:
                if x == 'liberal':
                    await president.send(file = discord.File(f'cogs/picture/{pics_used[0]}/liberal.{pics_used[1]}'))
                elif x == 'fascist':
                    await president.send(file = discord.File(f'cogs/picture/{pics_used[0]}/fascist.{pics_used[1]}'))
            return
        elif game_obj.return_presidential_power() == 'Identity':
            await self._channel.send('The President can investigate another players Identity')
            player = await self.SH_investigate(game_obj, game_obj.return_president())
            await self._channel.send(f'{president.name} investigated {player.name} party membership')
        elif game_obj.return_presidential_power() == 'President':
            await self._channel.send('The President can choose the next presidential candidate')
            player = await self.SH_make_next_president(game_obj)
            await self._channel.send(f'{president.name} chose {player.name} as the next president candidate')
        elif game_obj.return_presidential_power() == 'Kill':
            #await self._channel.send('The President Must kill a player')
            member, hitler_lost = await self.SH_execution(game_obj)
            await self._channel.send(f'{president.name} killed {member.name}')
            self._vc.play(discord.FFmpegPCMAudio('cogs/Meme/coffin_dance.mp3'))
            if hitler_lost:
                await self._channel.send('The liberals won, by killing Hitler!')
                return True
        return False


    async def SH_veto(self,game_obj, president,chancellor,policies):
        if game_obj._passed_policies[1] == 5:
            veto = await chancellor.send('The Veto power has been unlocked, do you want to reject these policies?')
            await veto.add_reaction('👍')
            await veto.add_reaction('👎')
            reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction,user: self.check_vote(reaction,user,chancellor,veto.id))
            if (reaction.emoji == '👍'):
                await self._channel.send('The Chancellor requested Veto')
                veto_check = await president.send('The Chancellor used his veto, do you accept it?')
                await veto_check.add_reaction('👍')
                await veto_check.add_reaction('👎')
                reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction,user: self.check_vote(reaction,user,president,veto_check.id))
                if (reaction.emoji == '👍'):
                    for x in policies:
                        game_obj.discard_card(x)
                    return True
                await self._channel.send('The President rejected the Veto')
                await chancellor.send('The President rejected your Veto, please cast your vote.')
        return False


    def write_safe_file(self,game_obj):
        safe_data = game_obj.return_safe_data()
        f = open("SH/SH_safe_file", "w")
        for x in safe_data:
            f.write(f)
        f.close()


    @commands.command(brief='Recover the last SH game', description = 'The Game saves a game copy on each new round, which will be recover when using this command')
    await def recover_game_SH(self, ctx):
        self._SH_game = self.SH_game(self._players)
        f = open("SH/SH_safe_file", "r")

        f.close()
        self._channel.send("Game recovered")
        await self.SH_next_round()





def setup(client):
    client.add_cog(SH(client))

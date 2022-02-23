# Importing some stuff
import discord
from discord.commands import slash_command, Option
from discord.ui import Button, View
from discord.ext import commands
import spotipy
from spotipy.oauth2 import *
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch
from pytube import YouTube as pyt
import youtube_dl
from lyrics_extractor import SongLyrics
import json
import os
from random import *
from alive import *
import asyncio
from dotenv import load_dotenv
# Declaring the bot variable
bot = discord.Bot()

# Secret Variables thingy#
load_dotenv('secrets.env')

my_secret = os.getenv('TOKEN')

json_api_key = os.getenv('json_api_key')
gcs_genius_engineid = os.getenv('gcs_genius_engineid')

sp_clientid = os.getenv('sp_clientid')
sp_clientsecret = os.getenv('sp_clientsecret')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=sp_clientid, client_secret=sp_clientsecret))


################################################################################################
# Cog #
################################################################################################

# Making and inherting a class from commands.Cog


class slash_cog(commands.Cog):
    # The extremely standard __init__ function with some variables declared
    def __init__(self, bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {
                            'format': 'bestaudio',
                            'noplaylist': 'True'
                            }
        self.FFMPEG_OPTIONS = {
            'before_options':
                '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        self.vc = ""

    # searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item,
                                        download=False)['entries'][0]

            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    # What's next?
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            print(self.music_queue)
            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @slash_command(name="play", description="Plays audio from YouTube")
    async def play(self, ctx, audio: Option(str, "The title to search for", required = True)):
        await ctx.defer()

        voice_state = ctx.author.voice
        if voice_state is None:
            await ctx.respond("Connect to a voice channel!")
        else:
            # if (ctx.author == "Abhishek Saxena ()"):
            #         await ctx.respond("RICKLOCKED 🔐\nNo more rickrolls allowed")
            voice_channel = ctx.author.voice.channel

            song = self.search_yt(audio)
            if type(song) == type(True):
                await ctx.respond(
                    "Could not play the audio. Incorrect format, try another keyword. This could be due to a playlist or livestream format, or because of some internal error."
                )
            else:
                self.music_queue.append([song, voice_channel])

                # await ctx.respond(
                #     f"Song added to the queue, just for you {ctx.author.mention}")

                self.personal_embed = discord.Embed(
                    title="Audio added to Queue", color=0xFF0000)

                if self.is_playing == False:
                    await self.play_music()

                results = YoutubeSearch(audio, max_results=1).to_dict()

                yt_link = f"https://www.youtube.com/watch?v={results[0]['id']}"

                yt_video_info = pyt(yt_link)

                self.personal_embed.add_field(
                    name=":adult: Audio playing for:", value=ctx.author.mention)

                self.personal_embed.add_field(
                    name=":musical_note: Audio:", value=f"[{yt_video_info.title}]({yt_link})", inline=False)

                self.personal_embed.add_field(name=":hourglass_flowing_sand: Duration:",
                                              value=f"{yt_video_info.length // 60} min {yt_video_info.length % 60} s", inline=False)

                self.personal_embed.add_field(
                    name=":eye: Views (on YouTube):", value=f"{format(int(yt_video_info.views),',d')}", inline=False)

                self.personal_embed.set_thumbnail(
                    url=yt_video_info.thumbnail_url)

                self.personal_embed.set_author(
                    name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80")

                await ctx.respond(embed=self.personal_embed)

    @slash_command(name="lyrics", description="Shows the lyrics of a song")
    async def lyrics(self, ctx, song: Option(str, "The song you want to find the lyrics of", required = True)):
        await ctx.defer()
        extract_lyrics = SongLyrics(json_api_key, gcs_genius_engineid)

        try:
            lyrics = extract_lyrics.get_lyrics(song)

            my_embed = discord.Embed(title=lyrics['title'],
                                     description=lyrics['lyrics'])

        except Exception:
            error = "Lyrics not found. Try reframing the song title and/or check if the song even exists or you or I have ascended into a parallel universe (or multiple for that matter). If that's the case, we're trying our best to contact Emu Lords to give their nails to scrape this configuration off.\n\n**Thanks!**\nTeam AxC"

            my_embed = discord.Embed(title=":octagonal_sign:  Error",
                                     description=error)

        await ctx.respond("Here are the lyrics!")
        await ctx.respond(embed=my_embed)

    @slash_command(name="queue", description="Displays the current songs in queue")
    async def queue(self, ctx):
        await ctx.defer()
        if len(self.music_queue) <= 21:
            retval = ""
            for i in range(len(self.music_queue)):
                retval += self.music_queue[i][0]['title'] + "\n"

            print(retval)

            if retval != "":
                await ctx.respond(retval)
                await ctx.respond('https://tenor.com/view/squid-game-netflix-egybest-film-squid-gif-23324577')
            else:
                await ctx.respond("No music in queue")

        else:
            retval = ""
            for i in range(len(self.music_queue)):
                for _ in range(21):
                    retval += self.music_queue[i][0]['title'] + "\n"
                    await ctx.respond(retval)
                retval = ""
            await ctx.respond("https://tenor.com/view/squid-game-netflix-egybest-film-squid-gif-23324577")

            print(retval)

    @slash_command(name="skip", description="Skips the audio being played and plays the next audio in the queue")
    async def skip(self, ctx):
        await ctx.defer()
        if self.vc != "" and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music()

            self.personal_embed = discord.Embed(
                title="Skipped the Audio", color=discord.Color.gold())
            self.personal_embed.set_author(
                name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=80&q=80")

            await ctx.respond(embed=self.personal_embed)

    @slash_command(name="disconnect", description="Disconnects the bot from the voice channel")
    async def disconnect(self, ctx):
        await ctx.defer()
        # await ctx.voice_client.disconnect()

        if self.vc != "":
            await self.vc.disconnect(force=True)

            self.dc_embed = discord.Embed(
                title="Disconnected 🔇", color=discord.Color.red())
            self.dc_embed.set_author(
                name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=80&q=80")

            await ctx.respond(embed=self.dc_embed)

        else:
            await ctx.respond("Bot not in any voice channel")

    @slash_command(name="pause", description="Pauses the audio")
    async def pause(self, ctx):
        await ctx.defer()
        # voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)

        if self.vc != "":
            self.vc.pause()

            self.pause_embed = discord.Embed(
                title="Paused ⏸", color=discord.Color.blue())
            self.pause_embed.set_author(
                name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=80&q=80")

            await ctx.respond(embed=self.pause_embed)

        else:
            await ctx.respond("No audio being played")

        # ctx.voice_client.pause()

    @slash_command(name="resume", description="Resumes the audio")
    async def resume(self, ctx):
        await ctx.defer()

        if self.vc != "":
            self.vc.resume()

            self.resume_embed = discord.Embed(
                title="Resumed ⏯", color=discord.Color.green())
            self.resume_embed.set_author(
                name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=80&q=80")

            await ctx.respond(embed=self.resume_embed)

        else:
            await ctx.respond("No audio being played")

    @slash_command(name="stop", description="Stops the audio")
    async def stop(self, ctx):
        await ctx.defer()
        # ctx.voice_client.stop()

        if self.vc != "":
            self.vc.stop()

            self.stop_embed = discord.Embed(
                title="Stopped 🛑", color=discord.Color.red())
            self.stop_embed.set_author(
                name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=80&q=80")

            await ctx.respond(embed=self.stop_embed)

        else:
            await ctx.respond("No audio being played")

    @slash_command(name="url", description="Plays the audio of the provided YouTube URL")
    async def url(self, ctx, url: Option(str, "The YouTube URL you want to play", required = True)):
        await ctx.defer()
        if ctx.author.voice is None:
            await ctx.respond("You're not in a voice channel")

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()

        else:
            await ctx.voice_client.move_to(voice_channel)

        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {
            'before_options':
                '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(
                url2, **FFMPEG_OPTIONS)
            await ctx.respond("Playing the URL in the voice channel")
            vc.play(source)

    @slash_command(name="loop", description="Loops audio n number of times (n is user-defined, defaults to 10)")
    async def loop(self, ctx, audio: Option(str, "The audio you want to loop", required = True), looping_constant: Option(int, "No. of times you want to loop the audio (defaults to 10)", required = False, default = 10)):
        await ctx.defer()
        voice_state = ctx.author.voice

        if voice_state is None:
            # you need to be connected so that the bot knows where to go
            await ctx.respond("Connect to a voice channel!")

        else:
            voice_channel = ctx.author.voice.channel

            song = self.search_yt(audio)

            if type(song) == type(True):
                await ctx.respond(
                    "Could not play the song. Incorrect format try another keyword. This could be due to a playlist or a livestream format."
                )

            else:
                for _ in range(looping_constant + 1):
                    self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music()
                
                self.personal_embed = discord.Embed(title="Loopin' it up! :musical_note: :loop:", color=0xFF0000)

                results = YoutubeSearch(audio, max_results=1).to_dict()

                yt_link = f"https://www.youtube.com/watch?v={results[0]['id']}"

                yt_video_info = pyt(yt_link)

                self.personal_embed.add_field(
                    name=":adult: Audio playing for:", value=ctx.author.mention)

                self.personal_embed.add_field(
                    name=":musical_note: Audio:", value=f"[{yt_video_info.title}]({yt_link})", inline=False)

                self.personal_embed.add_field(name=":hourglass_flowing_sand: Duration:",
                                              value=f"{(yt_video_info.length * looping_constant) // 60} min {(yt_video_info.length * looping_constant) % 60} s total\n({yt_video_info.length // 60} min {yt_video_info.length % 60} s each)", inline=False)

                self.personal_embed.add_field(
                    name=":eye: Views (on YouTube):", value=f"{format(int(yt_video_info.views),',d')}", inline=False)

                self.personal_embed.set_thumbnail(
                    url=yt_video_info.thumbnail_url)

                self.personal_embed.set_author(
                    name="AxC 777 Music", icon_url="https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80")

                await ctx.respond(embed=self.personal_embed)



                    
    @slash_command(name="clear", description="Clears the queue")
    async def clear(self, ctx):
        await ctx.defer()
        if self.vc != "" and self.vc:
            self.vc.stop()

            for _ in range(len(self.music_queue)):
                self.music_queue.pop()

            x = randrange(1, 3)

            await ctx.respond("Queue Cleared!")
            await ctx.respond(
                "https://tenor.com/view/were-all-clear-yellowstone-were-good-to-go-ready-lets-do-this-gif-17723207" if x == 1 else "https://tenor.com/view/squid-game-netflix-gif-23230821"
            )

        else:
            await ctx.respond("No audio in the queue")
            
    @slash_command(name="top_tracks", description="Shows the top tracks of an artist")
    async def top_tracks(self, ctx, artist: Option(str, "The artist you want to find the top tracks of", required = True)):
        await ctx.defer()
        results = sp.search(q=artist, limit=10, type="track")

        self.my_embed = discord.Embed(title=f"Top tracks of {artist.title()}", color=0x00ff00)

        for idx, track in enumerate(results['tracks']['items']):
            min_sec = divmod(track['duration_ms'] / 1000, 60)

            self.my_embed.add_field(
                name=f"{idx + 1}. {track['name']}", value=f"**Duration:** {int(min_sec[0])} min {round(min_sec[1],2)} s", inline=False)

        # print(results)

        await ctx.respond(embed=self.my_embed)

    @slash_command(name="latency", description="Shows the latency of the bot")
    async def latency(self, ctx):
        await ctx.defer()

        await ctx.respond(f"The latency of the bot is {bot.latency * 1000} ms")
        
################################################################################################
# Running the bot and stuff #
################################################################################################


@bot.event
async def on_ready():
    for please in range(len(bot.guilds)):
        print(bot.guilds[please])

    print(f"\n{len(bot.guilds)} servers")


async def ch_pr():
    await bot.wait_until_ready()
    statuses = [f"{len(bot.guilds)} servers | / cmds", f"{len(bot.guilds)} servers | ?switch", "Rick Roll | / cmds"]

    while not bot.is_closed():
        main_status = random.choice(statuses)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=main_status))

        await asyncio.sleep(10)

bot.loop.create_task(ch_pr())

bot.add_cog(slash_cog(bot))


bot.run(my_secret)

import discord
from discord.ext import commands
from youtube_dl import YoutubeDL


class Music(commands.Cog):
    def __init__(self, chatot):
        self.bot = chatot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.ydl_options = {
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
            'no-playlist': True
        }

        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.ydl_options) as ydl:
            # noinspection PyBroadException
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            murl = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(murl, **self.ffmpeg_options), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            murl = self.music_queue[0][0]['source']

            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.vc.play(discord.FFmpegPCMAudio(murl, **self.ffmpeg_options), after=lambda e: self.play_next())
            await ctx.send("gm")
        else:
            self.is_playing = False

    @commands.command(name="join", aliases=["j"], help="Joins the voice channel and prepares to play tunes.")
    async def join(self, ctx):
        self.vc.connect()

    @commands.command(name="play", aliases=["p"], help="Searches for the track and plays it if successful.")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # executes if user is not connected to a voice channel
            await ctx.send("You must be connected to a voice channel first!")
        else:
            song = self.search_yt(query)
            await ctx.send("Track added to the queue.")
            self.music_queue.append([song, voice_channel])

            if self.is_playing is False:
                await self.play_music(ctx)

    @commands.command(name="pause", aliases=["pa"], help="Pauses the track Chatot is playing.")
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.send("Track paused.")
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.send("Track resumed.")

    @commands.command(name="resume", aliases=["r"], help="Resumes the track Chatot was playing.")
    async def resume(self, ctx):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            await ctx.send("Track resumed.")

    @commands.command(name="skip", aliases=["s"], help="Skips the track currently being played.")
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            # attempt to play next song in queue
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the track(s) currently in the queue.")
    async def queue(self, ctx):
        if len(self.music_queue) == 0:
            return await ctx.send("There are no tracks currently in the queue.")
        else:
            embed = discord.Embed(
                title="Track Queue",
                description="",
                color=discord.Color.lighter_gray()
            )
            i = 0
            for track in self.music_queue:
                embed.description += f"**{i})** {track[0]['title']}\n"
                i += 1
            await ctx.send(embed=embed)

    @commands.command(name="clear", aliases=["c"], help="Clears the queue and lowers the stress level of Chatot.")
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Queue cleared.")

    @commands.command(name="leave", aliases=["l"], help="Removes Chatot from the voice call.")
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        self.vc.stop()
        await self.vc.disconnect()
        await ctx.send("gn")

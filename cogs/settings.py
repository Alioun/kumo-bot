from discord.ext import commands
from tinydb import TinyDB, Query


class SettingsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('db.json')
        self.announce_table = self.db.table('announcements')
        self.feed_table = self.db.table('feeds')
        self.chapter_table = self.db.table('chapters')
        self.tweet_table = self.db.table('tweets')
        self.query = Query()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix):
        query_res = self.db.search(
            (self.query.type == 'bot_channel') & (self.query.bot_channel_id == ctx.channel.id) & (
                    self.query.guild_id == ctx.guild.id))
        if query_res:
            self.bot.command_prefix = prefix
            await ctx.send(f'Prefix successfully changed to: {prefix}')
        else:
            await ctx.send('Command not allowed in this channel.')

    @commands.command(name='sam')
    @commands.has_permissions(administrator=True)
    async def set_announce_manga(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'Manga', notif_channel, notif_role, discuss_channel)

    @commands.command(name='saln')
    @commands.has_permissions(administrator=True)
    async def set_announce_light_novel(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'Light Novel', notif_channel, notif_role, discuss_channel)

    @commands.command(name='sawn')
    @commands.has_permissions(administrator=True)
    async def set_announce_web_novel(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'Web Novel', notif_channel, notif_role, discuss_channel)

    @commands.command(name='saa')
    @commands.has_permissions(administrator=True)
    async def set_announce_anime(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'Anime', notif_channel, notif_role, discuss_channel)

    @commands.command(name='sfm')
    @commands.has_permissions(administrator=True)
    async def set_feed_manga(self, ctx, feed_url):
        await self.set_feed(ctx, 'Manga', feed_url)

    @commands.command(name='sfln')
    @commands.has_permissions(administrator=True)
    async def set_feed_light_novel(self, ctx, feed_url):
        await self.set_feed(ctx, 'Light Novel', feed_url)

    @commands.command(name='sfwn')
    @commands.has_permissions(administrator=True)
    async def set_feed_web_novel(self, ctx, feed_url):
        await self.set_feed(ctx, 'Web Novel', feed_url)

    @commands.command(name='sbc')
    @commands.has_permissions(administrator=True)
    async def set_bot_channel(self, ctx, bot_channel):
        channel_id = int(bot_channel[2:-1])

        query_res = self.db.search((self.query.type == 'bot_channel') & (self.query.guild_id == ctx.guild.id))
        if not query_res:
            self.db.insert({'type': 'bot_channel', 'bot_channel_id': channel_id, 'guild_id': ctx.guild.id})
            await ctx.send(f'Successfully set bot channel channel to {bot_channel}')
        else:

            self.db.update({'bot_channel_id': channel_id}, (self.query.type == 'bot_channel')
                           & (self.query.guild_id == ctx.guild.id))
            await ctx.send(f'Bot Channel updated to {bot_channel}')

    @commands.command(name='lac')
    @commands.has_permissions(administrator=True)
    async def list_announce_channels(self, ctx):
        announce_items = self.announce_table.all()
        msg = '**ID** » Type | Announcement Channel | Role | Discuss Channel\n'
        msg = msg + '--------------------------------------------------\n'
        for item in announce_items:
            if item['guild_id'] == ctx.guild.id:
                msg = msg + f'**{item["id"]}** » ' \
                    f'{item["type"]} | ' \
                    f'<#{item["notif_channel_id"]}> | ' \
                    f'<@&{item["role_id"]}> | ' \
                    f'<#{item["discuss_channel_id"]}>\n'
        await ctx.send(msg)

    @commands.command(name='lf')
    @commands.has_permissions(administrator=True)
    async def list_feeds(self, ctx):
        feed_items = self.feed_table.all()
        msg = '**ID** » Type | Feed URL\n'
        msg = msg + '-----------------------\n'
        for item in feed_items:
            if item['guild_id'] == ctx.guild.id:
                msg = msg + f'**{item["id"]}** » {item["type"]} | {item["feed_url"]}\n'
        await ctx.send(msg)

    @commands.command(name='dac')
    @commands.has_permissions(administrator=True)
    async def delete_announce_channel(self, ctx, id):
        id = int(id)
        doc = self.announce_table.get(doc_id=id)
        if doc and doc.get('guild_id') == ctx.guild.id:
            self.announce_table.remove(doc_ids=[id])
            await ctx.send(f'Successfully deleted channel with ID **{id}**.')
        else:
            await ctx.send(f'Wrong ID.')

    @commands.command(name='df')
    @commands.has_permissions(administrator=True)
    async def delete_feed(self, ctx, id):
        id = int(id)
        doc = self.feed_table.get(doc_id=id)
        if doc and doc.get('guild_id') == ctx.guild.id:
            self.feed_table.remove(doc_ids=[id])
            await ctx.send(f'Successfully deleted feed with ID **{id}**.')
        else:
            await ctx.send(f'Wrong ID.')

    async def set_announce(self, ctx, type, notif_channel, notif_role, discuss_channel):
        notif_channel_id = int(notif_channel[2:-1])
        role_id = int(notif_role[3:-1])
        discuss_channel_id = int(discuss_channel[2:-1])

        query_res = self.announce_table.search((self.query.type == type)
                                               & (self.query.notif_channel_id == notif_channel_id)
                                               & (self.query.role_id == role_id)
                                               & (self.query.guild_id == ctx.guild.id))
        if not query_res:
            id = self.announce_table.insert({'type': type, 'notif_channel_id': notif_channel_id, 'role_id': role_id,
                                             'discuss_channel_id': discuss_channel_id, 'guild_id': ctx.guild.id})
            self.announce_table.update({'id': id}, (self.query.type == type)
                                       & (self.query.notif_channel_id == ctx.channel.id)
                                       & (self.query.guild_id == ctx.guild.id)
                                       & (self.query.role_id == role_id))
            await ctx.send(
                f'Successfully set **{type}** announcement channel to {notif_channel}.'
                f'\nNotification role has been set to <@&{role_id}>.'
                f'\nDiscussion channel set to {discuss_channel}')
        else:
            await ctx.send('Channel and Role were already set.')

    async def set_feed(self, ctx, type, feed_url):

        query_res = self.feed_table.search((self.query.type == type)
                                           & (self.query.feed_url == feed_url)
                                           & (self.query.guild_id == ctx.guild.id))
        if not query_res:
            id = self.feed_table.insert({'type': type, 'feed_url': feed_url, 'guild_id': ctx.guild.id})
            self.feed_table.update({'id': id}, (self.query.type == type)
                                   & (self.query.feed_url == feed_url)
                                   & (self.query.guild_id == ctx.guild.id))
            await ctx.send(f'Successfully set **{type}** feed with {feed_url}')
        else:
            await ctx.send('Feed was already set.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("Insufficient permissions!")


def setup(bot):
    bot.add_cog(SettingsCog(bot))

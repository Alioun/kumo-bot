from discord.ext import commands
from tinydb import TinyDB, Query


class SettingsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('db.json')

    @commands.command()
    async def prefix(self, ctx, prefix):
        query = Query()
        query_res = self.db.search(
            (query.type == 'bot_channel') & (query.channel_id == ctx.channel.id) & (query.guild_id == ctx.guild.id))
        if query_res:
            self.bot.command_prefix = prefix
            await ctx.send(f'Prefix successfully changed to: {prefix}')
        else:
            await ctx.send('Command not allowed in this channel.')

    @commands.command(name='sam')
    async def set_announce_manga(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'manga', notif_channel, notif_role, discuss_channel)

    @commands.command(name='saln')
    async def set_announce_light_novel(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'light novel', notif_channel, notif_role, discuss_channel)

    @commands.command(name='sawn')
    async def set_announce_web_novel(self, ctx, notif_channel, notif_role, discuss_channel):
        await self.set_announce(ctx, 'web novel', notif_channel, notif_role, discuss_channel)

    @commands.command(name='sbc')
    async def set_bot_channel(self, ctx, bot_channel):
        channel_id = int(bot_channel[2:-1])
        query = Query()
        query_res = self.db.search((query.type == 'bot_channel') & (query.guild_id == ctx.guild.id))
        if not query_res:
            self.db.insert({'type': 'bot_channel', 'channel_id': channel_id, 'guild_id': ctx.guild.id})
            await ctx.send(f'Successfully set bot channel channel to {bot_channel}')
        else:

            self.db.update({'channel_id': channel_id}, (query.type == 'bot_channel') & (query.guild_id == ctx.guild.id))
            await ctx.send(f'Bot Channel updated to {bot_channel}')

    async def set_announce(self, ctx, type, notif_channel, notif_role, discuss_channel):
        notif_channel_id = int(notif_channel[2:-1])
        role_id = int(notif_role[3:-1])
        discuss_channel_id = int(discuss_channel[2:-1])
        query = Query()
        query_res = self.db.search(
            (query.type == type) & (query.channel_id == notif_channel_id) & (query.role_id == role_id))
        if not query_res:
            self.db.insert({'type': type, 'notif_channel_id': notif_channel_id, 'role_id': role_id,
                            'discuss_channel_id': discuss_channel_id})
            await ctx.send(
                f"Successfully set **{type}** announcement channel to {notif_channel}."
                f"\nNotification role has been set to <@&{role_id}>."
                f"\nDiscussion channel set to {discuss_channel}")
        else:
            await ctx.send("Channel and Role were already set.")


def setup(bot):
    bot.add_cog(SettingsCog(bot))

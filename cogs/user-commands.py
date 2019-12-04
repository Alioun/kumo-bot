from discord.ext import commands
import feedparser
from tinydb import TinyDB, Query


class UserCommandsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('db.json')
        self.announce_table = self.db.table('announcements')
        self.feed_table = self.db.table('feeds')
        self.chapter_table = self.db.table('chapters')
        self.tweet_table = self.db.table('tweets')
        self.query = Query()

    @commands.command(name='test_report')
    async def test_report(self, ctx, rss, request_type, content_name):
        await self.report_update(feedparser.parse(rss).entries[0], Query(), request_type, content_name)


    @commands.command(name='lcm')
    async def latest_manga_chapter(self, ctx):
        query = Query()
        query_res = self.chapter_table.search((query.type == 'Manga'))
        if query_res:
            await ctx.send(f"{query_res[0]['title']}: is the latest chapter in the series \n\n{query_res[0]['link']}")
        else:
            await ctx.send(f"We currently have no information on the latest chapter ... Nai Wa~")


    @commands.command(name='lcln')
    async def latest_light_novel_chapter(self, ctx):
        query = Query()
        query_res = self.chapter_table.search((query.type == 'Light Novel'))
        if query_res:
            await ctx.send(f"{query_res[0]['title']}: is the latest chapter in the series \n\n{query_res[0]['link']}")
        else:
            await ctx.send(f"We currently have no information on the latest chapter ... Nai Wa~")


    @commands.command(name='lcwn')
    async def latest_web_novel_chapter(self, ctx):
        query = Query()
        query_res = self.chapter_table.search((query.type == 'Web Novel'))
        if query_res:
            await ctx.send(f"{query_res[0]['title']}: is the latest chapter in the series \n\n{query_res[0]['link']}")
        else:
            await ctx.send(f"We currently have no information on the latest chapter ... Nai Wa~")

def setup(bot):
    bot.add_cog(UserCommandsCog(bot))
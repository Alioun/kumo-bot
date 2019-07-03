import sys
import traceback

from discord.ext import commands
import feedparser
import asyncio
from tinydb import TinyDB, Query


class MangaCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('db.json')
        self.bot.bg_task = self.bot.loop.create_task(self.chapter_check_bg())
        self.update_time = 30

    @commands.command(name='test_announce')
    async def test_announce(self, ctx, rss, request_type, content_name):
        await self.announce_update(feedparser.parse(rss).entries[0], Query(), request_type, content_name)

    @commands.command(name='lcm')
    async def latest_manga_chapter(self, ctx):
        query = Query()
        query_res = self.db.table('chapters').search((query.type == 'Manga'))
        if query_res:
            await ctx.send(f"{query_res[0]['title']}: is the latest chapter in the series \n\n{query_res[0]['link']}")
        else:
            await ctx.send(f"We currently have no information on the latest chapter")

    @commands.command(name='lcln')
    async def latest_light_novel_chapter(self, ctx):
        query = Query()
        query_res = self.db.table('chapters').search((query.type == 'Light Novel'))
        if query_res:
            await ctx.send(f"{query_res[0]['title']}: is the latest chapter in the series \n\n{query_res[0]['link']}")
        else:
            await ctx.send(f"We currently have no information on the latest chapter")

    @commands.command(name='lcwn')
    async def latest_web_novel_chapter(self, ctx):
        query = Query()
        query_res = self.db.table('chapters').search((query.type == 'Web Novel'))
        if query_res:
            await ctx.send(f"{query_res[0]['title']}: is the latest chapter in the series \n\n{query_res[0]['link']}")
        else:
            await ctx.send(f"We currently have no information on the latest chapter")

    async def chapter_check_bg(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                manga_rss = self.find_feed('Manga')
                wn_rss = self.find_feed('Web Novel')
            except Exception:
                print(f'There was a problem finding feeds', file=sys.stderr)
                await asyncio.sleep(self.update_time)
                continue
            for rss_feed in manga_rss:
                await self.chapter_check(rss_feed['feed_url'], "chapters", "announcements", "Manga")
            for rss_feed in wn_rss:
                await self.chapter_check(rss_feed['feed_url'], "chapters", "announcements", "Web Novel")
            await asyncio.sleep(self.update_time)

    async def chapter_check(self, rss, content_type, request_type, content_name):
        rss = feedparser.parse(rss)
        chapter = ''
        if content_name == 'Web Novel':
            for update in rss.entries:
                if 'kumo desu' in update.title.lower():
                    chapter = update
                    break
        else:
            chapter = rss.entries[0]
        if chapter == '':
            return
        query = Query()
        query_res = self.db.table(content_type).search((query.type == content_name) & (query.title == chapter.title))
        if not query_res:
            await self.set_latest(query, content_type, content_name, chapter.title , chapter.link)
            await self.announce_update(chapter, query, request_type, content_name)
        else:
            await self.set_latest(query, content_type, content_name, rss.entries[0].title , rss.entries[0].link)

    async def announce_update(self, chapter, query, request_type, content_name):
        query_res = self.db.table(request_type).search((query.type == content_name))
        if query_res:
            for channel in query_res:
                cha = self.bot.get_channel(channel['notif_channel_id'])
                await cha.send(
                    f"***<@&{channel['role_id']}>***\n\n\n{chapter.title}:** has been translated and "
                    f"released on MangaDex! Discussion of the new chapter will take place in "
                    f"<#{channel['discuss_channel_id']}> or the stickied post on Reddit. "
                    f"\n\n<https://www.reddit.com/r/KumoDesu>**\n\n\n{chapter.link}\n\n")

    async def set_latest(self, query, content_type, content_name, title, link):
        query_res = self.db.table(content_type).search((query.type == content_name))
        if not query_res:
            self.db.table(content_type).insert({'type': content_name, 'title': title, 'link': link})
        else:
            self.db.table(content_type).update({'title': title, 'link': link}, (query.type == content_name))

    def find_feed(self, feed_type):
        feed = self.db.table('feeds').search((Query().type == feed_type))
        try:
            if not feed:
                raise LookupError('Could not find suitable feed')
            else:
                return feed
        except LookupError as e:
            print(f'{e.args}', file=sys.stderr)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(MangaCog(bot))

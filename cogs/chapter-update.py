import sys
import traceback

from discord.ext import commands
import feedparser
import asyncio
from tinydb import TinyDB, Query
from .reports import ReportsCog


class ChapterUpdateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('db.json')
        self.announce_table = self.db.table('announcements')
        self.feed_table = self.db.table('feeds')
        self.chapter_table = self.db.table('chapters')
        self.tweet_table = self.db.table('tweets')
        self.bot.bg_task = self.bot.loop.create_task(self.chapter_check_bg())
        self.update_time = 1
        self.query = Query()

    async def chapter_check_bg(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                manga_rss = self.find_feed('Manga')
                manga_spin_off_rss = self.find_feed('Manga Spin-Off')
                wn_rss = self.find_feed('Web Novel')
            except Exception:
                print(f'There was a problem finding feeds', file=sys.stderr)
                await asyncio.sleep(self.update_time)
                continue
            for rss_feed in manga_rss:
                await self.chapter_check(rss_feed['feed_url'], "chapters", "announcements", "Manga")
            for rss_feed in manga_spin_off_rss:
                await self.chapter_check(rss_feed['feed_url'], "chapters", "announcements", "Manga Spin-Off")
            for rss_feed in wn_rss:
                await self.chapter_check(rss_feed['feed_url'], "chapters", "announcements", "Web Novel")
            await asyncio.sleep(self.update_time)

    async def chapter_check(self, rss, content_type, request_type, content_name):
        rss = feedparser.parse(rss)
        chapter = ''
        if content_name == 'Web Novel':
            for update in rss.entries :
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
            await self.set_latest(query, content_type, content_name, chapter.title, chapter.link)
            await ReportsCog.report_update(self, chapter, query, request_type, content_name)
        else:
            await self.set_latest(query, content_type, content_name, rss.entries[0].title, rss.entries[0].link)

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
    bot.add_cog(ChapterUpdateCog(bot))

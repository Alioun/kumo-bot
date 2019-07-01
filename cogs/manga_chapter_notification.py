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
        self.manga_rss = 'https://mangadex.org/rss/wRFyMxNqKYevsgmkEUQ5VrXBWZd6zpuT/manga_id/17709'
        self.wn_rss = 'https://rtd.moe/feed/'
        self.bot.bg_task = self.bot.loop.create_task(self.chapter_check_bg())

    @commands.command(name='test_announce')
    async def test_announce(self, ctx, channel_type, rss):
        await self.announce_update(feedparser.parse(rss).entries[0], Query(), channel_type)

    async def chapter_check_bg(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.chapter_check(self.manga_rss, 'manga_chapter', 'manga')
            await self.chapter_check(self.wn_rss, 'wn_chapter', 'web_novel')
            await asyncio.sleep(20)

    async def chapter_check(self, rss, chapter_type, channel_type):
        rss = feedparser.parse(rss)
        chapter = ''
        try:
            if chapter_type == 'wn_chapter':
                for update in rss.entries:
                    if 'kumo desu' in update.title.lower():
                        chapter = update
                        break
            else:
                chapter = rss.entries[0]
            if chapter == '':
                return
        except Exception:
            print(f'Failed to set the chapter name.', file=sys.stderr)
            traceback.print_exc()
        query = Query()
        query_res = self.db.search((query.type == chapter_type) & (query.title == chapter.title))
        if not query_res:
            try:
                await self.set_latest(query, chapter_type, chapter.title)
                await self.announce_update(chapter, query, channel_type)
            except Exception:
                print(f'Failed to set the chapter and send it.', file=sys.stderr)
                traceback.print_exc()
        else:
            await self.set_latest(query, chapter_type, rss.entries[0].title)

    async def announce_update(self, chapter, query, channel_type):
        query_res = self.db.search((query.type == channel_type))
        if query_res:
            try:
                for channel in query_res:
                    cha = self.bot.get_channel(channel['channel_id'])
                    await cha.send(
                        f"***<@&{channel['role_id']}>***\n\n\n{chapter.title}:** has been translated and "
                        f"released on MangaDex! Discussion of the new chapter will take place in "
                        f"<#{channel['channel_id']}> or the stickied post on Reddit. "
                        f"\n\n<https://www.reddit.com/r/KumoDesu>**\n\n\n{chapter.link}\n\n")
            except Exception:
                print(f'Failed to print.', file=sys.stderr)
                traceback.print_exc()

    async def set_latest(self, query, chapter_type, title):
        query_res = self.db.search((query.type == chapter_type))
        if not query_res:
            self.db.insert({'type': chapter_type, 'title': title})
        else:
            self.db.update({'title': title}, (query.type == chapter_type))


def setup(bot):
    bot.add_cog(MangaCog(bot))

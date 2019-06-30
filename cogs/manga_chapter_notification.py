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
        self.bot.bg_task = self.bot.loop.create_task(self.manga_bg())

    @commands.command(name='manga')
    async def manga(self, ctx):
        rss = feedparser.parse(self.manga_rss)
        await ctx.send(f'**{rss.entries[0].title}:**\n\n{rss.entries[0].link}\n\n**')

    async def manga_bg(self):
        await self.bot.wait_until_ready()
        rss = feedparser.parse(self.manga_rss)
        while not self.bot.is_closed():
            query = Query()
            query_res = self.db.search((query.type == 'manga_chapter') & (query.title == rss.entries[0].title))
            if not query_res:
                try:
                    await self.set_latest(query, 'manga_chapter', rss.entries[0].title)
                    await self.announce_update(rss, query)
                except Exception:
                    print(f'Failed to set the chapter and send it.', file=sys.stderr)
                    traceback.print_exc()
            else:
                await self.set_latest(query, 'manga_chapter', rss.entries[0].title)

            await asyncio.sleep(10)

    async def announce_update(self, rss, query):
        query_res = self.db.search((query.type == 'manga'))
        if query_res:
            try:
                for channel in query_res:
                    cha = self.bot.get_channel(channel['channel_id'])
                    await cha.send(
                        f"***<@&{channel['role_id']}> REJOICE , FOR THERE IS A NEW CHAPTER***\n\n\n{rss.entries[0].title}:**\n\n\n{rss.entries[0].link}\n\n**")
            except Exception:
                print(f'Failed to print.', file=sys.stderr)
                traceback.print_exc()

    async def set_latest(self, query, type, title):
        query_res = self.db.search((query.type == 'manga_chapter'))
        if not query_res:
            self.db.insert({'type': type, 'title': title})
        else:
            self.db.update({'title': title}, (query.type == 'manga_chapter'))


def setup(bot):
    bot.add_cog(MangaCog(bot))

from discord.ext import commands
from tinydb import TinyDB, Query


class ReportsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('db.json')
        self.announce_table = self.db.table('announcements')
        self.feed_table = self.db.table('feeds')
        self.chapter_table = self.db.table('chapters')
        self.tweet_table = self.db.table('tweets')
        self.query = Query()

    async def report_update(self, chapter, query, request_type, content_name):
        query_res = self.db.table(request_type).search((query.type == content_name))
        if query_res:
            for channel in query_res:
                cha = self.bot.get_channel(channel['notif_channel_id'])
                if content_name is 'Manga' or 'Manga Spin-Off':
                    if int(channel['silence']) > 0:
                        self.announce_table.update({'silence': int(channel['silence']) - 1},
                                                   (self.query.type == content_name))
                    else:
                        await cha.send(
                            f"***<@&{channel['role_id']}>***\n\n\n{chapter.title}:** has been translated and "
                            f"released on MangaDex! Discussion of the new chapter will take place in "
                            f"<#{channel['discuss_channel_id']}> or the stickied post on Reddit. "
                            f"\n\n<https://www.reddit.com/r/KumoDesu>**\n\n\n{chapter.link}\n\n")
                elif content_name is 'Web Novel':
                    if int(channel['silence']) > 0:
                        self.announce_table.update({'silence': int(channel['silence']) - 1},
                                                   (self.query.type == content_name))
                    else:
                        await cha.send(
                            f"***<@&{channel['role_id']}>***\n\n\n{chapter.title}:** has been translated and "
                            f"released on Raising the Dead's website! Discussion of the new chapter will take place in "
                            f"<#{channel['discuss_channel_id']}> or the stickied post on Reddit. "
                            f"\n\n<https://www.reddit.com/r/KumoDesu>**\n\n\n{chapter.link}\n\n")
                elif content_name is 'Light Novel':
                    if int(channel['silence']) > 0:
                        self.announce_table.update({'silence': int(channel['silence']) - 1},
                                                   (self.query.type == content_name))
                    else:
                        await cha.send(
                            f"***<@&{channel['role_id']}>***\n\n\n{chapter.title}:** has been translated and "
                            f"on sale on Amazon! Discussion of the new Volume will take place in "
                            f"<#{channel['discuss_channel_id']}> or the stickied post on Reddit. "
                            f"\n\n<https://www.reddit.com/r/KumoDesu>**\n\n\n{chapter.link}\n\n")

def setup(bot):
    bot.add_cog(ReportsCog(bot))

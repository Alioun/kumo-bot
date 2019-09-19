from discord.ext import commands
import tweepy
import asyncio
from tinydb import TinyDB, Query


class TemplateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.query = Query()
        self.db = TinyDB('db.json')
        f = open('twitter_auth', 'r')
        consumer_key = f.readline()[:-1]
        consumer_secret = f.readline()[:-1]
        access_token = f.readline()[:-1]
        access_token_secret = f.readline()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.tweet_track_table = self.db.table('tweet_track')
        self.announce_table = self.db.table('announcements')
        self.api = tweepy.API(auth)

        self.bot.bg_task = self.bot.loop.create_task(self.bg_task())
        self.update_time = 30

    @commands.command(name='sth')
    @commands.has_permissions(administrator=True)
    async def set_twitter_hash(self, ctx, hash):
        if not hash.startswith('#'):
            hash = '#' + hash
        query_res = self.tweet_track_table.search((self.query.type == 'hash') & (self.query.value == hash))
        if not query_res:
            id = self.tweet_track_table.insert({'type': 'hash', 'value': hash})
            self.tweet_track_table.update({'id': id, 'guild_id': ctx.guild.id}, doc_ids=[id])
            await ctx.send(f'Tracking **{hash}**.')
        else:
            await ctx.send(f'Already tracking **{hash}**.')

    @commands.command(name='stu')
    @commands.has_permissions(administrator=True)
    async def set_twitter_user(self, ctx, screen_name):
        if screen_name.startswith('@'):
            screen_name = screen_name[1:]
        query_res = self.tweet_track_table.search((self.query.type == 'user') & (self.query.value == screen_name))
        if not query_res:
            id = self.tweet_track_table.insert({'type': 'user', 'value': screen_name})
            self.tweet_track_table.update({'id': id, 'guild_id': ctx.guild.id}, doc_ids=[id])
            await ctx.send(f'Tracking **{screen_name}**.')
        else:
            await ctx.send(f'Already tracking **{screen_name}**.')

    async def get_tweets(self):
        docs = self.tweet_track_table.all()
        tweet_urls = []
        try:
            for doc in docs:
                last_update_since_id = 0
                if doc.get('last_update_since_id'):
                    print(f"Getting newest tweets for {doc['value']}.")
                    if doc.get('type') == 'hash':
                        for tweet in tweepy.Cursor(self.api.search, q=doc.get('value'),
                                                   since_id=doc.get('last_update_since_id'),
                                                   result_type='recent').items():
                            url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                            tweet_urls.append(url)
                            if tweet.id > last_update_since_id:
                                last_update_since_id = tweet.id
                        if last_update_since_id:
                            self.tweet_track_table.update({'last_update_since_id': last_update_since_id},
                                                          doc_ids=[doc['id']])
                    elif doc.get('type') == 'user':
                        for tweet in tweepy.Cursor(self.api.user_timeline, screen_name=doc.get('value'),
                                                   since_id=doc.get('last_update_since_id')).items():
                            url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                            tweet_urls.append(url)
                            if tweet.id > last_update_since_id:
                                last_update_since_id = tweet.id
                        if last_update_since_id:
                            self.tweet_track_table.update({'last_update_since_id': last_update_since_id},
                                                          doc_ids=[doc['id']])
                else:
                    print(f"Getting since_id for {doc['value']}.")
                    if doc.get('type') == 'hash':
                        for tweet in tweepy.Cursor(self.api.search, q=doc.get('value'), result_type='recent').items(1):
                            if tweet.id > last_update_since_id:
                                last_update_since_id = tweet.id
                        if last_update_since_id:
                            self.tweet_track_table.update({'last_update_since_id': last_update_since_id},
                                                          doc_ids=[doc['id']])
                    elif doc.get('type') == 'user':
                        for tweet in tweepy.Cursor(self.api.user_timeline, screen_name=doc.get('value')).items(1):
                            if tweet.id > last_update_since_id:
                                last_update_since_id = tweet.id
                        if last_update_since_id:
                            self.tweet_track_table.update({'last_update_since_id': last_update_since_id},
                                                          doc_ids=[doc['id']])
        except tweepy.error.TweepError:
            print("Rate limited, try again later.")

        return tweet_urls

    async def bg_task(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            tweet_urls = await self.get_tweets()
            query_res = self.announce_table.search((self.query.type == 'Twitter'))
            if query_res:
                for channel in query_res:
                    cha = self.bot.get_channel(channel['notif_channel_id'])
                    for url in tweet_urls:
                        await cha.send(url)
            await asyncio.sleep(self.update_time)

    @commands.command(name='stc')
    @commands.has_permissions(administrator=True)
    async def set_twitter_channel(self, ctx, notif_channel):
        notif_channel_id = int(notif_channel[2:-1])
        query_res = self.announce_table.search((self.query.type == 'Twitter')
                                               & (self.query.notif_channel_id == notif_channel_id)
                                               & (self.query.guild_id == ctx.guild.id))
        if not query_res:
            id = self.announce_table.insert(
                {'type': 'Twitter', 'notif_channel_id': notif_channel_id, 'guild_id': ctx.guild.id})
            self.announce_table.update({'id': id}, (self.query.type == 'Twitter')
                                       & (self.query.notif_channel_id == ctx.channel.id)
                                       & (self.query.guild_id == ctx.guild.id))
            await ctx.send(
                f'Successfully set **Twitter** announcement channel to {notif_channel}.')
        else:
            await ctx.send('Channel was already set.')

    @commands.command(name='lt')
    @commands.has_permissions(administrator=True)
    async def list_twitter(self, ctx):
        tracked_items = self.tweet_track_table.all()
        msg = '**ID** » Type | Value\n'
        msg = msg + '-----------------------\n'
        for item in tracked_items:
            if item['guild_id'] == ctx.guild.id:
                msg = msg + f'**{item["id"]}** » {item["type"]} | {item["value"]}\n'
        await ctx.send(msg)

    @commands.command(name='dt')
    @commands.has_permissions(administrator=True)
    async def delete_twitter(self, ctx, id):
        id = int(id)
        doc = self.tweet_track_table.get(doc_id=id)
        if doc and doc.get('guild_id') == ctx.guild.id:
            self.tweet_track_table.remove(doc_ids=[id])
            await ctx.send(f'Successfully deleted feed with ID **{id}**.')
        else:
            await ctx.send(f'Wrong ID.')


def setup(bot):
    bot.add_cog(TemplateCog(bot))

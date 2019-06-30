import sys
import traceback

from discord.ext import commands
from discord import Colour
from discord import Embed

initial_extensions = ['cogs.wiki',
                      'cogs.settings',
                      'cogs.manga_chapter_notification']

bot = commands.Bot(command_prefix='-')
bot.remove_command('help')

# load the extensions(cogs) listed above in [initial_extensions]
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def help(ctx):
    embed = Embed(colour=Colour.dark_red())

    embed.set_author(name='Help')
    embed.add_field(name=bot.command_prefix + 'sam <notification channel> <notification role> <discussion channel>',
                    value='Set where to send notifications when a new Manga chapter drops, together with a role that get\'s notified and a channel where discussions can be held.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'saln <notification channel> <notification role> <discussion channel>',
                    value='Set where to send notifications when a new Light Novel Volume drops, together with a role that get\'s notified and a channel where discussions can be held.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'sawn <notification channel> <notification role> <discussion channel>',
                    value='Set where to send notifications when a new Web Novel chapter drops, together with a role that get\'s notified and a channel where discussions can be held.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'saa <notification channel> <notification role> <discussion channel>',
                    value='Set where to send notifications when a new Anime Episode drops, together with a role that get\'s notified and a channel where discussions can be held.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'lac', value='List all set announcement channels.', inline=False)
    embed.add_field(name=bot.command_prefix + 'dac <ID>', value='Delete an announcement channel with the given ID.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'sfm <feed url>', value='Set Manga rss feed to check for updates.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'sfln <feed url>', value='Set Light Novel rss feed to check for updates.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'sfwn <feed url>', value='Set Web Novel rss feed to check for updates.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'lf', value='List all set feeds.', inline=False)
    embed.add_field(name=bot.command_prefix + 'df <ID>', value='Delete a feed with the given ID.', inline=False)
    embed.add_field(name=bot.command_prefix + 'prefix <prefix>', value='Change the prefix for the commands.',
                    inline=False)
    embed.add_field(name=bot.command_prefix + 'kw <search phrase>',
                    value='Search the kumo wiki and return the post summary.', inline=False)
    await ctx.send(embed=embed)


# get bot token
f = open('bot_token', 'r')
token = f.readline()

# init bot
bot.run(token)

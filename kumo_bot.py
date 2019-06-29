import sys
import traceback

from discord.ext import commands

initial_extensions = ['cogs.wiki',
                      'cogs.settings']

bot = commands.Bot(command_prefix='-')

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


# get bot token
f = open('bot_token', 'r')
token = f.readline()

# init bot
bot.run(token)

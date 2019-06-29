from discord.ext import commands


class SettingsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prefix(self, ctx, prefix):
        # todo add permission check or bot specific channel,
        # where the bot sends administrative messages to and where this command is allowed
        self.bot.command_prefix = prefix
        await ctx.send(f'Prefix successfully changed to: {prefix}')


def setup(bot):
    bot.add_cog(SettingsCog(bot))

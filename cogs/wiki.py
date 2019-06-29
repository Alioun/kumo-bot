from discord.ext import commands


class WikiCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kw(self, ctx, article):
        await ctx.send(f'Kumo wiki response for article: {article}')


def setup(bot):
    bot.add_cog(WikiCog(bot))

from discord.ext import commands


class TemplateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='templatecmd')
    async def template_cmd(self, ctx, arg):
        await ctx.send(f'template {arg}')


def setup(bot):
    bot.add_cog(TemplateCog(bot))

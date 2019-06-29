from discord.ext import commands
import wikia


class WikiCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.wiki = "kumodesu"

    @commands.command()
    async def kw(self, ctx, articles):
        page = wikia.page(self.wiki, articles)
        if page.summary.lower().startswith("redirect"):
            redirect = " ".join(page.summary.split(" ")[1:])
            page = wikia.page(self.wiki, redirect)

        summary = page.content.split("\n")[0]
        await ctx.send(f'**{page.title}:**\n\n{summary}\n\n*{"_".join(page.url.split(" "))}*')


def setup(bot):
    bot.add_cog(WikiCog(bot))

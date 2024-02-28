from __future__ import annotations
from typing import TYPE_CHECKING

import disnake
from disnake.ext import commands

if TYPE_CHECKING:
    from utils.client import BotCore


class GuildCheck(commands.Cog):

    def __init__(self, bot: BotCore):
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def guild_add(self, g: disnake.Guild):

        if not self.bot.pool.config["SILENT_PUBLICBOT_WARNING"]:

            appinfo = await self.bot.application_info()

            if not appinfo.bot_public:
                return

            try:
                owners = appinfo.team.members
            except AttributeError:
                owners = [appinfo.owner]

            for owner_id in self.bot.env_owner_ids:
                if u := self.bot.get_user(owner_id):
                    owners.append(u)

            if [dev for dev in owners if self.check_member(dev, g)]:
                return

            guild_count = 1

            for guild in self.bot.guilds:

                if guild == g:
                    continue

                if not [dev for dev in owners if self.check_member(dev, guild)]:

                    if guild_count <= 2:
                        guild_count += 1
                        continue

                    text = f"saí do servidor **{g.name} [{g.id}]** " \
                            "automaticamente devido a possível distribuição/diponibilidade pública...\n" \
                            "O bot que tiver usando essa source/code só pode ser adicionado em servidores pelo " \
                            "próprio dono do bot ou membro da equipe do bot (que estão listados no menu de team da " \
                            "aplicação no discord developer portal). O bot só pode ser adicionado em até " \
                            "**2 servidores por outros usuários**.\n" \
                            "Caso queira evitar que seu bot seja adicionado por qualquer usuário " \
                            "você pode desmarcar a opção \"public bot\" do seu bot no developer portal."

                    txt_owners = "Só será permitido a minha adição no server se pelo menos um dos " \
                                f"seguintes usuários tenham a permissão de **Gerenciar Servidor** no servidor " \
                                f"**{g.name}**: " + " ".join(o.mention for o in owners)

                    embed = disnake.Embed(
                        description=f"{text}\n\n### Nota:\n{txt_owners}", color=g.me.color
                    )
                    embed.set_author(name="Remoção automática de server")

                    if g.icon:
                        embed.set_thumbnail(url=g.icon.replace(static_format="png").url)

                    try:
                        await g.leave()
                    except:
                        pass
                    else:
                        print(text.replace(self.bot.user.mention, self.bot.user.display_name).replace("**", "**"))
                        for o in owners:
                            try:
                                await o.send(embed=embed)
                                break
                            except:
                                continue

    def check_member(self, u: disnake.User, g: disnake.Guild):
        member = g.get_member(u.id)
        return member and member.guild_permissions.manage_guild


def setup(bot: BotCore):
    bot.add_cog(GuildCheck(bot))


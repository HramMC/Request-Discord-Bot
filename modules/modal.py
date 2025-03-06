import disnake
from disnake.ext import commands
from disnake import TextInputStyle
import sqlite3

from pyexpat.errors import messages


# Подключение к базе данных и создание таблицы, если она не существует
def initialize_db():
    conn = sqlite3.connect('./data_base/requests.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  message_id INTEGER,
                  nickname TEXT,
                  status TEXT)''')
    conn.commit()
    conn.close()

# Инициализация базы данных при запуске
initialize_db()

class MyModal(disnake.ui.Modal, commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Ваш никнейм",
                placeholder="Dream_Craft2013",
                custom_id="Nickname",
                required=True,
                style=TextInputStyle.short,
                max_length=16,
            ),
            disnake.ui.TextInput(
                label="Возраст",
                placeholder="Ваш возраст",
                custom_id="Age",
                required=True,
                style=TextInputStyle.single_line,
            ),
            disnake.ui.TextInput(
                label="Знание правил",
                placeholder="На сколько хорошо вы знаете правила",
                custom_id="Know rules",
                required=True,
                style=TextInputStyle.single_line,
            ),
            disnake.ui.TextInput(
                label="Откуда узнали о проекте?",
                placeholder="Ник/Ссылка пригласившего",
                custom_id="Inviter",
                style=TextInputStyle.short,
            ),
        ]
        super().__init__(
            title="request",
            custom_id="create_request",
            timeout=120,
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        requestEmbed = disnake.Embed(
            title="Новая заявка!",
            description=f"**Отправитель: {inter.user.global_name}**",
            color=disnake.Colour.red(),
        )
        requestEmbed.set_thumbnail(url=inter.user.display_avatar.url)
        for key, value in inter.text_values.items():
            requestEmbed.add_field(
                name=key.capitalize(),
                value=value[:1024],
                inline=False,
            )
        await inter.response.send_message(content="Вы успешно заполнили анкету!", ephemeral=True)
        requestCallBackEmbed = disnake.Embed(
            title="Ваша заявка отправлена на рассмотрение!",
            description="***На рассмотрение заявок уходит до 24-х часов***",
            color=disnake.Colour.purple(),
        )
        requestCallBackEmbed.set_image(file=disnake.File("./ref/request.png"))
        confirmButton = disnake.ui.View()
        requestAcceptButton = disnake.ui.Button(
            style=disnake.ButtonStyle.green,
            label="Принять",
            custom_id="Accept",
        )
        confirmButton.add_item(requestAcceptButton)
        requestRejectButton = disnake.ui.Button(
            style=disnake.ButtonStyle.red,
            label="Отклонить",
            custom_id="Reject",
        )
        confirmButton.add_item(requestRejectButton)
        await inter.author.send(embed=requestCallBackEmbed)
        channel = self.bot.get_channel(1336306177469976659)
        db_bug = await channel.send(embed=requestEmbed, view=confirmButton)
        db_id = db_bug.id


        # Сохраняем данные в базу данных
        conn = sqlite3.connect('./data_base/requests.db')
        c = conn.cursor()
        c.execute("INSERT INTO requests (user_id, message_id, nickname, status) VALUES (?, ?, ?, ?)",
                  (inter.author.id, db_id, inter.text_values['Nickname'], 'pending'))
        conn.commit()
        conn.close()

    @commands.slash_command()
    async def requestslash(self, inter: disnake.AppCmdInter):
        await inter.response.send_modal(modal=MyModal(bot=self.bot))

def setup(bot: commands.Bot):
    bot.add_cog(MyModal(bot))
# -*- coding: utf-8 -*-

from nextcord.ext import commands
import nextcord
from nextcord.ui import Button, View
from nextcord.ext import commands
from config import token
from threading import Thread
from time import sleep

from ProgramPresets import programPreset

from youtube_dl import YoutubeDL

# блок с разрешениями бота
intents = nextcord.Intents.all()
# блок с разрешениями бота

bot = commands.Bot(command_prefix='m!', intents=intents)

music_preset = programPreset

YDL_OPTIONS = {'format': 'bestaudio/best', 'nopaylist': 'False', 'simulate': 'True', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


@bot.command(name='p')
async def play(ctx, url):
    """(p) можно использовать и ссылки на ютуб и поисковые запросы(без пробелов)"""
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in url:
            info = ydl.extract_info(url, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]

    link = info['formats'][0]['url']

    vc.play(nextcord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS))


class Urls(nextcord.ui.Modal):
    def __init__(self, mainView):
        super().__init__("Пользовательский набор")
        self.name = nextcord.ui.TextInput(label="Название набора", min_length=2, max_length=50, required=True)
        self.music = nextcord.ui.TextInput(label="ссылки", style=nextcord.TextInputStyle.paragraph,
                                           placeholder="введите ссылки через пробел", required=True, max_length=1800, )
        self.add_item(self.name)
        self.add_item(self.music)
        self.mainView = mainView

    async def callback(self, interaction: nextcord.Interaction) -> None:
        music_preset[self.name.value] = self.music.value
        await self.mainView.update(interaction)


class PresetSelectMenu(nextcord.ui.Select):
    def __init__(self, ctx):
        options = []
        self.ctx = ctx
        for key in music_preset.keys():
            options.append(nextcord.SelectOption(label=key))
        super().__init__(placeholder='Выберите набор для запуска', options=options)

    async def callback(self, interaction: nextcord.Interaction):
        await stop(self.ctx)
        await play(self.ctx, self.values[0])


class MainView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.add_item(PresetSelectMenu(ctx))

    @nextcord.ui.button(label='Добавить свой набор музыки', style=nextcord.ButtonStyle.green, row=0)
    async def user_button_callback(self, button, interaction):
        modal = Urls(self)
        await interaction.response.send_modal(modal)

    @nextcord.ui.button(label='Добавить набор из списка', style=nextcord.ButtonStyle.green, row=1)
    async def program_button_callback(self, button, interaction):
        pass

    async def update(self, interaction):
        await interaction.response.edit_message(view=MainView(self.ctx))


@bot.command()
async def preset(ctx):
    global name_channel, vc
    name_channel = ctx.author.voice.channel.name
    vc = await ctx.message.author.voice.channel.connect()
    main_view = MainView(ctx)
    await ctx.channel.send(f'{ctx.author.mention}, выберите вариант.', view=main_view)


@bot.command(name='pe')
async def pause(ctx):
    """(pe)ставит музыку на паузу"""
    if vc.is_playing():
        vc.pause()


@bot.command(name='l')
async def leave(ctx):
    """(l) выход из войса"""
    if vc.is_connected():
        await vc.disconnect()


@bot.command(name='re')
async def resume(ctx):
    """(re)снимает музыку с паузы"""
    if vc.is_paused():
        vc.resume()


@bot.command(name='s')
async def stop(ctx):
    """(s)останавливает музыку"""
    vc.stop()


bot.run(token)

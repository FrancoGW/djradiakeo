import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

# ============================================================
#  DJ Radiakeo - Bot de música para Discord
#  Comandos: !play, !skip, !pause, !resume, !stop, !queue, !np
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Estado por servidor
queues = {}      # guild_id -> deque de (title, url)
voice_clients = {}  # guild_id -> VoiceClient

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "opus",
    }],
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]


async def search_song(query: str):
    """Busca una canción en YouTube y devuelve (title, url_stream)."""
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch1",
        "noplaylist": True,
    }
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(query, download=False)
        )
    if "entries" in data:
        data = data["entries"][0]
    return data["title"], data["url"]


async def play_next(ctx, guild_id):
    """Reproduce la siguiente canción de la cola."""
    queue = get_queue(guild_id)
    if not queue:
        await ctx.send("🎵 **DJ Radiakeo** terminó la cola. ¡Poneme más música con `!play`!")
        return

    title, url = queue.popleft()
    vc = voice_clients.get(guild_id)
    if vc is None or not vc.is_connected():
        return

    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
    vc.play(
        discord.PCMVolumeTransformer(source, volume=0.7),
        after=lambda e: asyncio.run_coroutine_threadsafe(
            play_next(ctx, guild_id), bot.loop
        ),
    )
    await ctx.send(f"🎧 **DJ Radiakeo** está poniendo: **{title}**")


# ──────────────────────────────────────────────
#  EVENTOS
# ──────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ DJ Radiakeo conectado como {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="!play 🎶"
        )
    )


# ──────────────────────────────────────────────
#  COMANDOS
# ──────────────────────────────────────────────

@bot.command(name="play", aliases=["p"])
async def play(ctx, *, query: str):
    """Reproduce o agrega una canción a la cola. Uso: !play <nombre o URL>"""

    # Verificar que el usuario esté en un canal de voz
    if not ctx.author.voice:
        await ctx.send("❌ Tenés que estar en un canal de voz primero, pibe.")
        return

    guild_id = ctx.guild.id
    channel = ctx.author.voice.channel

    # Unirse al canal si no está
    vc = voice_clients.get(guild_id)
    if vc is None or not vc.is_connected():
        vc = await channel.connect(timeout=60.0, reconnect=True)
        voice_clients[guild_id] = vc
    elif vc.channel != channel:
        await vc.move_to(channel)

    await ctx.send(f"🔍 **DJ Radiakeo** buscando: `{query}`...")

    try:
        title, url = await search_song(query)
    except Exception as e:
        await ctx.send(f"❌ No pude encontrar esa canción. Error: {e}")
        return

    queue = get_queue(guild_id)

    if vc.is_playing() or vc.is_paused():
        queue.append((title, url))
        pos = len(queue)
        await ctx.send(f"➕ Agregado a la cola (posición {pos}): **{title}**")
    else:
        queue.append((title, url))
        await play_next(ctx, guild_id)


@bot.command(name="skip", aliases=["s", "next"])
async def skip(ctx):
    """Salta la canción actual. Uso: !skip"""
    vc = voice_clients.get(ctx.guild.id)
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭️ **DJ Radiakeo** saltó la canción.")
    else:
        await ctx.send("❌ No hay ninguna canción sonando.")


@bot.command(name="pause")
async def pause(ctx):
    """Pausa la reproducción. Uso: !pause"""
    vc = voice_clients.get(ctx.guild.id)
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️ Música pausada.")
    else:
        await ctx.send("❌ No hay ninguna canción sonando.")


@bot.command(name="resume", aliases=["r"])
async def resume(ctx):
    """Reanuda la reproducción. Uso: !resume"""
    vc = voice_clients.get(ctx.guild.id)
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶️ Retomando la música...")
    else:
        await ctx.send("❌ La música no está pausada.")


@bot.command(name="stop")
async def stop(ctx):
    """Detiene la música y limpia la cola. Uso: !stop"""
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if vc:
        get_queue(guild_id).clear()
        vc.stop()
        await vc.disconnect()
        voice_clients.pop(guild_id, None)
        await ctx.send("⏹️ **DJ Radiakeo** se fue a descansar. ¡Hasta luego!")
    else:
        await ctx.send("❌ No estoy en ningún canal de voz.")


@bot.command(name="queue", aliases=["q", "cola"])
async def queue_cmd(ctx):
    """Muestra la cola de canciones. Uso: !queue"""
    guild_id = ctx.guild.id
    queue = get_queue(guild_id)
    vc = voice_clients.get(guild_id)

    if not queue and (not vc or not vc.is_playing()):
        await ctx.send("📭 La cola está vacía.")
        return

    lines = ["🎶 **Cola de DJ Radiakeo:**\n"]
    for i, (title, _) in enumerate(queue, start=1):
        lines.append(f"**{i}.** {title}")

    if len(lines) == 1:
        lines.append("_(sin canciones en espera)_")

    await ctx.send("\n".join(lines))


@bot.command(name="np", aliases=["nowplaying", "actual"])
async def now_playing(ctx):
    """Muestra qué está sonando ahora. Uso: !np"""
    vc = voice_clients.get(ctx.guild.id)
    if vc and vc.is_playing():
        await ctx.send("🎵 **DJ Radiakeo** está poniendo música. Usá `!queue` para ver la cola.")
    else:
        await ctx.send("😴 **DJ Radiakeo** no está poniendo nada ahora.")


@bot.command(name="dj")
async def dj_info(ctx):
    """Info sobre DJ Radiakeo."""
    embed = discord.Embed(
        title="🎧 DJ Radiakeo",
        description="¡El mejor DJ del server! Siempre listo para poner la mejor música.",
        color=0xFF6B35,
    )
    embed.add_field(
        name="Comandos",
        value=(
            "`!play <canción>` — Poner música\n"
            "`!skip` — Saltar canción\n"
            "`!pause` / `!resume` — Pausar/Reanudar\n"
            "`!stop` — Parar todo\n"
            "`!queue` — Ver la cola\n"
            "`!np` — Qué está sonando\n"
        ),
        inline=False,
    )
    embed.set_footer(text="Hecho con ❤️ | DJ Radiakeo siempre prende el ambiente 🔥")
    await ctx.send(embed=embed)


# ──────────────────────────────────────────────
#  MANEJO DE ERRORES
# ──────────────────────────────────────────────

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Falta un argumento. Ejemplo: `!play nunca es suficiente`")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Error: {error}")
        raise error


# ──────────────────────────────────────────────
#  INICIO
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: No encontré el token. Configurá la variable DISCORD_TOKEN.")
        print("   Ejemplo: export DISCORD_TOKEN='tu_token_aqui'")
        exit(1)
    bot.run(token)
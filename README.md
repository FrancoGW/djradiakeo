# 🎧 DJ Marcelo — Bot de Música para Discord

El mejor DJ del server. Pone música de YouTube directo en tu canal de voz.

---

## 📋 Requisitos

- Python 3.10 o superior
- **FFmpeg** instalado en el sistema
- Una cuenta de Discord y un bot creado en el Portal de Desarrolladores

---

## ⚙️ Instalación paso a paso

### 1. Instalar FFmpeg

**Windows:**
1. Descargá FFmpeg desde https://ffmpeg.org/download.html
2. Extraé la carpeta y agregá la carpeta `bin` al PATH del sistema
3. Verificá con: `ffmpeg -version`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**macOS:**
```bash
brew install ffmpeg
```

---

### 2. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

---

### 3. Crear el bot en Discord

1. Entrá a https://discord.com/developers/applications
2. Hacé clic en **New Application** → ponele nombre (ej: "DJ Marcelo")
3. Andá a la sección **Bot** → clic en **Add Bot**
4. En **Privileged Gateway Intents**, activá:
   - ✅ MESSAGE CONTENT INTENT
5. Copiá el **Token** del bot (lo vas a necesitar)

---

### 4. Invitar el bot al servidor

1. Andá a **OAuth2 → URL Generator**
2. En **Scopes**, marcá: `bot`
3. En **Bot Permissions**, marcá:
   - ✅ Send Messages
   - ✅ Connect
   - ✅ Speak
   - ✅ Use Voice Activity
   - ✅ Read Message History
4. Copiá la URL generada y abrila en el navegador para invitar el bot

---

### 5. Configurar el token

**Linux/macOS:**
```bash
export DISCORD_TOKEN="tu_token_aqui"
```

**Windows (CMD):**
```cmd
set DISCORD_TOKEN=tu_token_aqui
```

**Windows (PowerShell):**
```powershell
$env:DISCORD_TOKEN="tu_token_aqui"
```

> También podés crear un archivo `.env` con `DISCORD_TOKEN=tu_token` y usar `python-dotenv`.

---

### 6. Ejecutar el bot

```bash
python bot.py
```

Si todo está bien vas a ver:
```
✅ DJ Marcelo conectado como DJ Marcelo#1234
```

---

## 🎵 Comandos

| Comando | Descripción |
|---------|-------------|
| `!play <canción o URL>` | Pone una canción o la agrega a la cola |
| `!skip` | Salta la canción actual |
| `!pause` | Pausa la reproducción |
| `!resume` | Reanuda la reproducción |
| `!stop` | Para todo y desconecta el bot |
| `!queue` | Muestra la cola de canciones |
| `!np` | Qué está sonando ahora |
| `!dj` | Info y lista de comandos |

---

## 💡 Ejemplos de uso

```
!play never gonna give you up
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!play cumbias para el asado
!skip
!queue
```

---

## 🛠️ Solución de problemas

**Error: `ffmpeg not found`**
→ FFmpeg no está instalado o no está en el PATH. Seguí el paso 1.

**Error: `opus library not found`**
→ Instalá libopus:
- Linux: `sudo apt install libopus-dev`
- macOS: `brew install opus`

**El bot se une pero no reproduce nada**
→ Verificá que FFmpeg esté correctamente instalado.

**Error de token**
→ Regenerá el token en el Portal de Desarrolladores y actualizá la variable de entorno.

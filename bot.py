import discord
from discord.ext import commands
from dotenv import load_dotenv

import os
import random
import datetime

# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

TOKEN = os.getenv("TOKEN")

# -----------------------------------
# BOT SETUP
# -----------------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='$',
    intents=intents
)

# -----------------------------------
# DATA COLLECTIONS
# -----------------------------------

roasts = [
    "You're proof that WiFi signals can suffer too.",
    "I'd explain it better, but I left my crayons at home.",
    "You type like your keyboard is fighting back.",
    "Bro argues with auto-correct and still loses.",
    "Your IQ looking like a loading screen stuck at 3%.",
    "You bring negative FPS to conversations.",
    "Your opinions are sponsored by lag.",
    "You're the human version of low battery mode."
]

songs = [
    "90210 - Travis Scott",
    "FE!N - Travis Scott",
    "Codeine Crazy - Future",
    "Stop Breathing - Playboi Carti",
    "Skyfall - Travis Scott",
    "Superhero - Metro Boomin",
    "DNA - Kendrick Lamar",
    "Family Ties - Baby Keem & Kendrick Lamar",
    "Nightcrawler - Travis Scott",
    "Mask Off - Future"
]

argument_starters = [
    "Nah you're actually wrong.",
    "That made absolutely zero sense.",
    "I disagree aggressively.",
    "Source: trust me bro?",
    "That's the dumbest thing I've heard today.",
    "Incorrect. Try again.",
    "You're chatting nonsense.",
    "Massive L take.",
    "Bro thought he cooked 💀",
    "Absolutely not."
]

argument_extras = [
    "Explain yourself immediately.",
    "I'm waiting for the logic here.",
    "You thought this was valid?",
    "This is why robots will replace humans.",
    "I refuse to believe someone typed this seriously.",
    "Even Google couldn't defend this take."
]

meme_gifs = [
    "https://media.giphy.com/media/10JhviFuU2gWD6/giphy.gif",
    "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif",
    "https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif",
    "https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif",
    "https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy.gif"
]

# -----------------------------------
# EVENTS
# -----------------------------------

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

# Automatic argument system
@bot.event
async def on_message(message):

    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Ignore commands
    if message.content.startswith('$'):
        await bot.process_commands(message)
        return

    # Random chance to argue
    chance = random.randint(1, 100)

    if chance <= 70:
        starter = random.choice(argument_starters)
        extra = random.choice(argument_extras)

        await message.reply(f"{starter} {extra}")

    await bot.process_commands(message)

# -----------------------------------
# COMMANDS
# -----------------------------------

# Roast command
@bot.command()
async def roast(ctx):
    await ctx.send(f"🔥 {random.choice(roasts)}")

# Meme command
@bot.command()
async def meme(ctx):
    await ctx.send(random.choice(meme_gifs))

# Daily song recommendation
@bot.command()
async def song(ctx):

    today = datetime.date.today()

    random.seed(today.toordinal())

    daily_song = random.choice(songs)

    await ctx.send(
        f"🎵 Daily Recommendation: **{daily_song}**"
    )

# Coin flip command
@bot.command()
async def coinflip(ctx):

    result = random.choice(["Heads", "Tails"])

    await ctx.send(f"🪙 {result}")

# Rate command
@bot.command()
async def rate(ctx, *, thing):

    score = random.randint(1, 10)

    await ctx.send(
        f"📊 I rate **{thing}** a solid **{score}/10**"
    )

# Motivation command
@bot.command()
async def motivate(ctx):

    messages = [
        "Get up and chase your goals before someone smarter does.",
        "You're either grinding or getting left behind.",
        "Wake up. Your competition isn't sleeping.",
        "Lock in before life humbles you.",
        "Even this bot believes in you more than you do."
    ]

    await ctx.send(f"💪 {random.choice(messages)}")

# Hot take command
@bot.command()
async def hottake(ctx):

    takes = [
        "Pineapple pizza is elite.",
        "Carti fans understand nothing and everything simultaneously.",
        "Dark mode should be legally mandatory.",
        "Spotify shuffle is fake.",
        "Chicken biryani > every food on Earth.",
        "Kendrick clears most rappers technically.",
        "Sleep is underrated for gym gains."
    ]

    await ctx.send(f"🗣️ HOT TAKE: {random.choice(takes)}")

# AI argument command
@bot.command()
async def argue(ctx, *, topic):

    responses = [
        f"Imagine believing '{topic}' is a good idea.",
        f"'{topic}' sounds like something invented during a power outage.",
        f"I'm automatically against '{topic}'.",
        f"You woke up and chose '{topic}'? Crazy.",
        f"Defending '{topic}' should require a license."
    ]

    await ctx.send(random.choice(responses))

# -----------------------------------
# START BOT
# -----------------------------------

bot.run(TOKEN)
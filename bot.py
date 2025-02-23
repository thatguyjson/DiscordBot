import nextcord
import mysql.connector
import asyncio
import time
import random
import requests
import json
import re
from nextcord.ext import commands, tasks
from nextcord.ui import View, Select
from datetime import datetime, timedelta, timezone
from constants import botToken

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix='?', intents=intents)

"""
big info section cause tee hee i love information so much!
"""

message_ids = {}
QOTD_CHANNEL_ID = 1299231913726312478
STAFF_CHANNEL_ID = 1299230783721967626
LOG_CHANNEL_ID = 1299264058436091915
ROLE_NAME = "*"
VerifyName = "Members"
ServerUpdateName = "Server Updates"
EventUpdateName = "Event Updates"
VerifyRole = "✅"
ServerUpdateRole = "✨"
EventUpdateRole = "☄️"
color_role = {
    1: ("Purple", "💜"),
    2: ("Orange", "🍊"),
    3: ("Aqua", "🌊"),
    4: ("PinkPastel", "🌸"),
    5: ("OrangePastel", "🟠"),
    6: ("Black", "🖤"),
    7: ("DeepPink", "💗"),
    8: ("Maroon", "💓")
}
README_URL = 'https://raw.githubusercontent.com/thatguyjson/DiscordBot/refs/heads/main/README.md'
dripMention = "<@639904427624628224>" # can use this in (f'x') text to @ myself in discord

def is_owner(ctx):
    role = nextcord.utils.get(ctx.guild.roles, name=ROLE_NAME)
    return role in ctx.author.roles or ctx.author.id == 542882947183673344

"""
DB stuff down below
"""
db = mysql.connector.connect(
    host="na04-sql.pebblehost.com",  # Example: "localhost" or "your-pebblehost-ip"
    user="customer_834000_DCBot1",
    password="Nc^QYdisxVFN884.0J5jYIZm",
    database="customer_834000_DCBot1",
    port=3306
)
cursor = db.cursor()


@bot.command()
@commands.check(is_owner)
async def add_question(ctx, *, question=None):
    if question:
      sql = "INSERT INTO QuotesDB (quotes) VALUES (%s)"
      val = (question,)
      cursor.execute(sql, val)
      db.commit()  # Save the changes to the database
      await ctx.send(f"Question added: {question}")
    else:
      await ctx.send("Please include a question in this format. ?add_question <Question>")

async def log_to_channel(message):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        utc_now = time.time()
        pacific_offset = -8 * 3600  # Standard PST offset
        if time.localtime(utc_now).tm_isdst == 0:  # Adjust for DST
            pacific_offset = -9 * 3600

        # Add 1 hour to the offset if required (testing or adjustments)
        pacific_offset += 1 * 3600

        # Convert UTC time to Pacific Time
        pacific_time = utc_now + pacific_offset
        timestamp = datetime.fromtimestamp(pacific_time).strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"**[{timestamp}]** {message}"
        await log_channel.send(log_message)

@bot.command()
@commands.check(is_owner)
async def readme(ctx):
    response = requests.get(README_URL)

    if response.status_code == 200:
        readme_content = response.text
        embed_title = "📄 GitHub README.md"
        embed_color = nextcord.Color.blue()

        # Split the README into chunks of 1000 chars (Discord embeds have a 1024-char limit per field)
        chunks = [readme_content[i:i+1000] for i in range(0, len(readme_content), 1000)]

        for index, chunk in enumerate(chunks):
            embed = nextcord.Embed(
                title=embed_title if index == 0 else None, 
                color=embed_color,
                description=chunk
            )
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Failed to fetch README.md file.")

@bot.command()
@commands.check(is_owner)
async def ping(ctx):
    latency_message = f'Ping: {round(bot.latency * 1000)} ms'
    await ctx.send(latency_message)
    await log_to_channel(latency_message)

@bot.event
async def on_member_join(member):
    if welcomeChannel is not None:
        message_type = random.randint(1, 11)
        messages = {
            1: f"DAMN {str(member.mention)} looks GOOD TODAY",
            2: f"{str(member.mention)} just joined! Hows it goin' cutie :3",
            3: f"{str(member.mention)} just fell from heaven. Oh how lucky we are",
            4: f"{str(member.mention)} looks absolutely stunning. Welcome!",
            5: f"{str(member.mention)} looks just like a dream, prettiest person we've ever seen",
            6: f"{str(member.mention)} has got to be the best looking person here :O",
            7: f"Hey {str(member.mention)}, whats cookin good lookin ; )",
            8: f"The way {str(member.mention)} joined the server. Very Demure. Very Mindful",
            9: f"{str(member.mention)} may look good, but can they handle this craziness? Welcome!",
            10: f"{str(member.mention)} kys",
            11: f"{str(member.mention)} lets have sex."
        }
        welcome_message = messages[message_type]
        await welcomeChannel.send(welcome_message)

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member is None or guild is None:
        return
    if payload.user_id == 1280817864357445663: #checks if bot
        return

    if payload.message_id == message_ids.get('verify_message_id') and str(payload.emoji) == VerifyRole:
        role = nextcord.utils.get(guild.roles, name=VerifyName)
        if role is not None:
            await member.add_roles(role)
            await log_to_channel(f'Assigned {VerifyName} to {member.display_name}')

    elif payload.message_id == message_ids.get('server_update_message_id') and str(payload.emoji) == ServerUpdateRole:
        role = nextcord.utils.get(guild.roles, name=ServerUpdateName)
        if role is not None:
            await member.add_roles(role)
            await log_to_channel(f"Assigned {ServerUpdateName} to {member.display_name}")

    elif payload.message_id == message_ids.get('event_update_message_id') and str(payload.emoji) == EventUpdateRole:
        role = nextcord.utils.get(guild.roles, name=EventUpdateName)
        if role is not None:
            await member.add_roles(role)
            await log_to_channel(f"Assigned {EventUpdateName} to {member.display_name}")
    elif payload.message_id == message_ids.get('color_message_id'):
        for role_name, emoji in color_role.values():
            if str(payload.emoji) == emoji:
                role = nextcord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                    await log_to_channel(f"Assigned {role_name} to {member.display_name}")
                break

@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member is None or guild is None:
        return
    if payload.user_id == 1280817864357445663: # checks if bot
        return

    if payload.message_id == message_ids.get('verify_message_id') and str(payload.emoji) == VerifyRole:
        role = nextcord.utils.get(guild.roles, name=VerifyName)
        if role is not None:
            await member.remove_roles(role)
            await log_to_channel(f'Removed {VerifyName} from {member.display_name}')

    elif payload.message_id == message_ids.get('server_update_message_id') and str(payload.emoji) == ServerUpdateRole:
        role = nextcord.utils.get(guild.roles, name=ServerUpdateName)
        if role is not None:
            await member.remove_roles(role)
            await log_to_channel(f"Removed {ServerUpdateName} from {member.display_name}")

    elif payload.message_id == message_ids.get('event_update_message_id') and str(payload.emoji) == EventUpdateRole:
        role = nextcord.utils.get(guild.roles, name=EventUpdateName)
        if role is not None:
            await member.remove_roles(role)
            await log_to_channel(f"Removed {EventUpdateName} from {member.display_name}")
    elif payload.message_id == message_ids.get('color_message_id'):
        for role_name, emoji in color_role.values():
            if str(payload.emoji) == emoji:
                role = nextcord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.remove_roles(role)
                    await log_to_channel(f"Removed {role_name} from {member.display_name}")
                break


@bot.command()
@commands.check(is_owner)
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: nextcord.Member = None, *, reason=None):
    if user == None:
        await ctx.send("Please enter a user!")
        return

    await user.kick(reason=reason)
    await ctx.send(f'Kicked {user.name} for reason: {reason}')

@bot.command()
@commands.check(is_owner)
@commands.has_permissions(ban_members=True)
async def evict(ctx, user: nextcord.Member = None, *, reason=None):
    if user == None:
        await ctx.send("Please enter a user!")
        return

    await user.ban(reason=reason)
    await ctx.send(f'Banned {user.name} for reason: {reason}')

@bot.command()
@commands.check(is_owner)
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: nextcord.Member = None, role: nextcord.Role = None):
    if member is None:
        await ctx.send("You need to specify a user!")
        return
    if role is None:
        await ctx.send("You need to specify a role!")
        return

    try:
        if role not in member.roles:
            await member.add_roles(role)
            await ctx.send(f"Successfully added {role.name} to {member.mention}!")
        else:
            await ctx.send(f"{member.mention} already has the {role.name} role.")
    except nextcord.Forbidden:
        await ctx.send("I don't have permission to manage roles.")
    except nextcord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def createuser(ctx,):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    NC_user_discord_id = ctx.author.id # grabs the users ID
    NC_user_name = ctx.author.name # grabs the users discord name
    NC_user_joined_at = str(ctx.author.joined_at) # grabs when the user joined the server // example data: 2021-05-01 12:34:56
    NC_user_created_at = str(ctx.author.created_at) # grabs when the user created their account // example data: 2021-05-01 12:34:56

    # User_gender grab
    await ctx.send("Please enter your gender (Male, Female, M, or F):")
    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        NC_user_gender = msg.content.lower()
        if NC_user_gender not in ["male", "female", "m", "f"]:
            await ctx.send("Invalid input. Please enter Male, Female, M, or F.")
            return
        if NC_user_gender == "m":
            NC_user_gender = "male"
        elif NC_user_gender == "f":
            NC_user_gender = "female"
        
        await ctx.send(f"Gender set to: {NC_user_gender.capitalize()} ✅")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond! ❌")
        return

    # user_pronouns grab
    await ctx.send(
        "Please enter the number corresponding to your pronouns:\n"
        "1️⃣ - He/Him\n"
        "2️⃣ - She/Her\n"
        "3️⃣ - He/They\n"
        "4️⃣ - She/They"
    )

    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        pronoun_choices = {"1": "He/Him", "2": "She/Her", "3": "He/They", "4": "She/They"}
        
        if msg.content not in pronoun_choices:
            await ctx.send("Invalid input. Please enter 1, 2, 3, or 4.")
            return

        NC_user_pronouns = pronoun_choices[msg.content]
        await ctx.send(f"Pronouns set to: {NC_user_pronouns} ✅")

    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond! ❌")
        return

    # User_age grab
    await ctx.send("Please respond with your age!")
    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        if len(msg.content) > 2:
            await ctx.send("Please enter a valid age.")
            return
        NC_user_age = msg.content
        await ctx.send(f"Set your age to {NC_user_age}!")

    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond! ❌")
        return

    
    # User_date_of_birth grab
    await ctx.send("Please enter your date of birth in the format YYYY-MM-DD:")

    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"

        if not re.match(date_pattern, msg.content):
            await ctx.send("Invalid format! Please enter your date of birth in YYYY-MM-DD format (e.g., 2000-05-15).")
            return

        NC_user_date_of_birth = msg.content
        await ctx.send(f"Date of birth set to: {NC_user_date_of_birth} ✅")

    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond! ❌")
        return

    
    try:
        cursor.execute(
            """
            INSERT INTO Users (user_discord_id, user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_joined_at, user_created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (NC_user_discord_id, NC_user_name, NC_user_gender, NC_user_pronouns, NC_user_age, NC_user_date_of_birth, NC_user_joined_at, NC_user_created_at),
        )

        db.commit()
        await ctx.send("User data successfully saved to the database! ✅")

    except Exception as e:
        await ctx.send(f"An error occurred while saving your data: {e}")

@bot.command()
async def praise(ctx, member: nextcord.Member = None):
    if member is None:
      await ctx.send("Please ping the user you wish to praise!")
    else:
      message_type = random.randint(1, 11)
      messages = {
              1: f"{member.mention}, you look so good right now.",
              2: f"{member.mention}, I love you.",
              3: f"{member.mention}, you deserve a gold star.",
              4: f"{member.mention}, youre quite the gem, a lovely one at that.",
              5: f"{member.mention}, you always brighten my day.",
              6: f"{member.mention}, good job kitten.",
              7: f"{member.mention}, you did a good job for daddy.",
              8: f"{member.mention}, lets shoot up a school together <3",
              9: f"{member.mention}, you can be my skibidi rizzler.",
              10: f"{member.mention}, I would choose you in a garden of roses.",
              11: f"{member.mention}, lets have sex."
        }
      await ctx.send(messages[message_type])

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    
    staff_channel = bot.get_channel(STAFF_CHANNEL_ID)
    if staff_channel:
        embed = nextcord.Embed(title="Message Deleted", color=nextcord.Color.red())
        embed.add_field(name="User", value=message.author.name, inline=True)
        embed.add_field(name="Channel", value=message.channel.name, inline=True)
        embed.add_field(name="Content", value=message.content or "No content", inline=False)
        await staff_channel.send(embed=embed)

# Task to check the time every minute
@tasks.loop(minutes=1)
async def qotd_task():
    """
    Task to send the Question of the Day (QOTD) at 6 AM PST daily.
    """
    try:
        # Calculate current Pacific Time (PST or PDT)
        utc_now = datetime.utcnow()
        pacific_offset = timedelta(hours=-8 if utc_now.timetuple().tm_isdst == 0 else -7)  # Adjust for DST
        pacific_time = utc_now + pacific_offset

        # Check if it's exactly 6:00 AM PST
        if pacific_time.hour == 6 and pacific_time.minute == 0:
            # Fetch a random question from the 'christmas' table
            cursor.execute("SELECT question FROM christmas ORDER BY RAND() LIMIT 1")
            question = cursor.fetchone()

            if not question:
                # If no questions in 'christmas', fallback to 'QuotesDB'
                cursor.execute("SELECT Quotes FROM QuotesDB ORDER BY RAND() LIMIT 1")
                question = cursor.fetchone()

            if question:
                question_text = question[0]  # Extract question text

                # Send the QOTD to the specified channel
                qotd_channel = bot.get_channel(QOTD_CHANNEL_ID)
                if qotd_channel:
                    await qotd_channel.send(
                        "@everyone\n🌟 **Question of the Day** 🌟\n{}".format(question_text)
                    )

                    # Move the used question to the appropriate table
                    if "christmas" in question:
                        cursor.execute("DELETE FROM christmas WHERE question = %s", (question_text,))
                    else:
                        cursor.execute("INSERT INTO UsedQuotesDB (UsedQuotes) VALUES (%s)", (question_text,))
                        cursor.execute("DELETE FROM QuotesDB WHERE Quotes = %s", (question_text,))
                    
                    db.commit()
            else:
                # Log if no questions are left in both tables
                await log_to_channel(
                    "<@639904427624628224> URGENT!!! No questions left in both 'christmas' and 'QuotesDB' tables!"
                )
        else:
            # Sleep asynchronously until the next minute
            await asyncio.sleep(60)
    except Exception as e:
        # Log errors for debugging
        await log_to_channel(f"Error in QOTD task: {e}")


@tasks.loop(hours=2)
async def keep_connection_alive():
    cursor.execute("SELECT UsedQuotes FROM UsedQuotesDB where id = 3")
    aliveQuote = cursor.fetchone()
    if aliveQuote:
      debug_channel = bot.get_channel(1307966892853432391)
      if debug_channel:
        await debug_channel.send(aliveQuote)

@bot.command()
@commands.check(is_owner)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please specify a positive number of messages to delete.", delete_after=5)
        return

    try:
        deleted = await ctx.channel.purge(limit=amount)
        confirmation = await ctx.send(f"✅ Deleted {len(deleted)} messages.", delete_after=5)
    except nextcord.Forbidden:
        await ctx.send("❌ I don't have permission to delete messages in this channel.", delete_after=5)
    except nextcord.HTTPException as e:
        await ctx.send(f"❌ An error occurred: {e}", delete_after=5)

@bot.command()
@commands.check(is_owner)
async def timepurge(ctx, amount: int, unit: str):
    """
    Purge messages from a channel based on a time period.
    Usage: ?purge <amount> <unit>
    Example: ?purge 1 hour
    """
    try:
        # Debug log for input
        await ctx.send(f"Debug: Received input - amount: {amount}, unit: {unit}")

        # Calculate the time threshold
        now = datetime.now(tz=timezone.utc)  # Offset-aware datetime
        if unit in ['minute', 'minutes']:
            threshold = now - timedelta(minutes=amount)
        elif unit in ['hour', 'hours']:
            threshold = now - timedelta(hours=amount)
        elif unit in ['day', 'days']:
            threshold = now - timedelta(days=amount)
        else:
            await ctx.send("Invalid time unit! Use 'minute', 'hour', or 'day'.")
            return

        # Debug log for calculated threshold
        await ctx.send(f"Debug: Calculated threshold: {threshold}")

        # Purge messages
        def check(msg):
            return msg.created_at >= threshold

        deleted = await ctx.channel.purge(check=check)
        await ctx.send(f"Deleted {len(deleted)} messages from the past {amount} {unit}(s).", delete_after=5)

    except ValueError:
        await ctx.send("Invalid input! Please ensure the amount is a number and the unit is a valid time unit.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@role.error
async def role_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Both a user and a role are required. Usage: `?role <user> <role>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Couldn't find the user or role. Please make sure they are valid.")

"""
down below is on_ready + bot.run
"""

@bot.event
async def on_ready():
    global welcomeChannel
    welcomeChannel = bot.get_channel(1280813683789791305)
    if welcomeChannel is None:
        await log_to_channel("Could not find the welcome channel.")
    else:
        await log_to_channel(f'Logged in as {bot.user.name}. Now commencing all startup processes. Please wait est: 25 seconds...') # time.sleep(x) multuplied by 5
        time.sleep(5)

    # Verify Roles Message
    channel1 = bot.get_channel(1280805997790887978)
    if channel1 is not None:
        try:
            await channel1.purge(limit=100)  # Limit the number of messages to purge
            verify_message = await channel1.send("React with ✅ to become a Tenant!")
            await verify_message.add_reaction("✅")
            message_ids["verify_message_id"] = verify_message.id
            await log_to_channel("Verify role setup complete.")
            time.sleep(5)
        except Exception as e:
            await log_to_channel(f"Error setting up verify role: {e}")

    # Server Updates and Event Updates Messages
    channel2 = bot.get_channel(1299261004169089066)
    if channel2 is not None:
        try:
            await channel2.purge(limit=100)
            server_update_message = await channel2.send("React with ✨ to gain the Server Updates Role")
            await server_update_message.add_reaction("✨")
            event_update_message = await channel2.send("React with ☄️ to gain the Event Updates Role")
            await event_update_message.add_reaction("☄️")

            message_ids["server_update_message_id"] = server_update_message.id
            message_ids["event_update_message_id"] = event_update_message.id
            await log_to_channel("Server Updates and Event Updates roles setup complete.")
            time.sleep(5)
        except Exception as e:
            await log_to_channel(f"Error setting up update roles: {e}")

    # Color Roles Message
    try:
        color_message = "\n".join([f"{emoji} - {role}" for role, emoji in color_role.values()])
        color_message_sent = await channel2.send(
            f"React to the image with the color you would like:\n**Available color roles:**\n{color_message}"
        )
        message_ids["color_message_id"] = color_message_sent.id

        for _, emoji in color_role.values():
            await color_message_sent.add_reaction(emoji)
            await asyncio.sleep(1)  # Add delay to avoid hitting rate limits
        time.sleep(8)
    except Exception as e:
        await log_to_channel(f"Error setting up color roles: {e}")
    qotd_task.start()
    await log_to_channel('started QOTD')
    time.sleep(5)
    keep_connection_alive.start()
    await log_to_channel('started task to keep DB connection alive.')
    time.sleep(5)
    await log_to_channel(f'{dripMention} BOT IS SET UP AND READY TO GO!')

bot.run(botToken)

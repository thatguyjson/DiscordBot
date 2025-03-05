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
from constants import DBhost, DBuser, DBpassword, DBdatabase, DBport

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
README_URL = 'https://raw.githubusercontent.com/thatguyjson/DiscordBot/refs/heads/master/README.md'
dripMention = "<@639904427624628224>" # can use this in (f'x') text to @ myself in discord
dripID = "639904427624628224"

def is_owner(ctx):
    role = nextcord.utils.get(ctx.guild.roles, name=ROLE_NAME)
    return role in ctx.author.roles or ctx.author.id == 542882947183673344

def is_drip(ctx):
    return ctx.author.id == 639904427624628224

"""
DB stuff down below
"""
db = mysql.connector.connect(
    host=DBhost,
    user=DBuser,
    password=DBpassword,
    database=DBdatabase,
    port=DBport
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
    try:
        response = requests.get(README_URL)

        # Check if the request was successful
        if response.status_code == 200:
            readme_content = response.text
            embed_color = nextcord.Color.blue()
            chunk_size = 1000  # Discord embed text size limit

            # Split the README into chunks of 1000 chars (Discord embeds have a 1024-char limit per field)
            chunks = [readme_content[i:i + chunk_size] for i in range(0, len(readme_content), chunk_size)]

            embed_title = "📄 GitHub README.md"

            # Send the first embed with title, then subsequent chunks without a title
            for index, chunk in enumerate(chunks):
                embed = nextcord.Embed(
                    title=embed_title if index == 0 else None, 
                    color=embed_color,
                    description=chunk
                )
                await ctx.send(embed=embed)

        else:
            await ctx.send(f"❌ Failed to fetch README.md file. HTTP Status: {response.status_code}")
    
    except requests.RequestException as e:
        # Catch request-related errors like network issues or invalid URL
        await ctx.send(f"❌ Error fetching the README.md: {str(e)}")

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
            10: f"{str(member.mention)} are you https? Because without you, im ://",
            11: f"Hey {str(member.mention)} if you were a vegetable, you'd be a cute-cumber."
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
async def createuser(ctx):
    if ctx.channel.id != 1343127549861167135:
        await ctx.send("Please go to <#1343127549861167135> to create your profile!")
        return
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    user_discord_id = ctx.author.id # grabs the users ID
    user_name = ctx.author.name # grabs the users discord name
    user_joined_at = str(ctx.author.joined_at)[:19] # grabs when the user joined the server // example data: 2021-05-01 12:34:56
    user_created_at = str(ctx.author.created_at)[:19] # grabs when the user created their account // example data: 2021-05-01 12:34:56

    # Blocks if the user already has a profile
    cursor.execute("SELECT 1 FROM Users WHERE user_discord_id = %s", (user_discord_id,))
    userCheck = cursor.fetchone()  # Fetch the first result
    if userCheck:
        await ctx.send(f'Hey <@{user_discord_id}>! You already have a profile. Please don\'t try creating more!')
        return

    
    # User_gender grab
    while True:
        await ctx.send("Please enter your gender (Male, Female, M,  F, NB, or NonBinary):")
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            user_gender = msg.content.lower()
            if user_gender not in ["male", "female", "m", "f", "nb", "nonbinary"]:
                await ctx.send("Invalid input. Please enter Male, Female, M,  F, NB, or NonBinary")
                continue  # Repeat the loop if input is invalid
            if user_gender == "m":
                user_gender = "male"
            elif user_gender == "f":
                user_gender = "female"
            elif user_gender == "nb" or "nonbinary":
                user_gender == "Non-Binary"

            await ctx.send(f"Gender set to: {user_gender.capitalize()} ✅")
            break  # Exit the loop if input is valid
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! ❌")
            return

    # user_pronouns grab
    while True:
        await ctx.send(
            "Please enter the number corresponding to your pronouns:\n"
            "1️⃣ - He/Him\n"
            "2️⃣ - She/Her\n"
            "3️⃣ - He/They\n"
            "4️⃣ - She/They\n"
            "5️⃣ - They/Them"
        )
    
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            pronoun_choices = {"1": "He/Him", "2": "She/Her", "3": "He/They", "4": "She/They", "5": "They/Them"}
            
            if msg.content not in pronoun_choices:
                await ctx.send("Invalid input. Please enter 1, 2, 3, 4, or 5.")
                continue
    
            user_pronouns = pronoun_choices[msg.content]
            await ctx.send(f"Pronouns set to: {user_pronouns} ✅")
            break
    
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! ❌")
            return

    # User_age grab
    while True:
        await ctx.send("Please respond with your age!")
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            if len(msg.content) > 2:
                await ctx.send("Please enter a valid age.")
                continue
            user_age = msg.content
            user_age = int(user_age)
            await ctx.send(f"Set your age to {user_age}!")
            break
    
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! ❌")
            return

    
    # User_date_of_birth grab
    while True:
        await ctx.send("Please enter your date of birth in the format YYYY-MM-DD:")
    
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    
            if not re.match(date_pattern, msg.content):
                await ctx.send("Invalid format! Please enter your date of birth in YYYY-MM-DD format (e.g., 2000-05-15).")
                continue
    
            user_date_of_birth = msg.content
            await ctx.send(f"Date of birth set to: {user_date_of_birth} ✅")
            break
    
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! ❌")
            return

    
    try:
        print(f"DEBUG: {user_discord_id}, {user_name}, {user_gender}, {user_pronouns}, {user_age}, {user_date_of_birth}, {user_joined_at}, {user_created_at}")
        cursor.execute(
            """
            INSERT INTO Users (user_discord_id, user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_joined_at, user_created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_discord_id, user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_joined_at, user_created_at),
        )


        db.commit()
        await ctx.send("User data successfully saved to the database! ✅")

    except Exception as e:
        await ctx.send(f"An error occurred while saving your data: {e}")

@bot.command()
async def updateuser(ctx):
    if ctx.channel.id != 1343127549861167135:
        await ctx.send("Please use <#1343127549861167135> for all commands related to user profiles!")
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    member = ctx.author.id
    # Blocks if the user if they dont have a profile
    cursor.execute("SELECT 1 FROM Users WHERE user_discord_id = %s", (member,))
    userCheck = cursor.fetchone()  # Fetch the first result
    if userCheck == None:
        await ctx.send(f'Hey <@{member}>! You dont have a profile. Please make one using ?createuser')
        return
    await ctx.send(
            f'Hey <@{member}>! What would you like to change about your profile?\n'
            "1️⃣ - Gender\n"
            "2️⃣ - Pronouns\n"
            "3️⃣ - Age\n"
            "4️⃣ - Birthday\n"
            "5️⃣ - Add a Profile Bio!"
        )
    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        if msg.content == "1":
            while True:
                await ctx.send("Please enter your preferred gender (Male, Female, M,  F, NB, or NonBinary):")
                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    user_gender = msg.content.lower()
                    if user_gender not in ["male", "female", "m", "f", "nb", "nonbinary"]:
                        await ctx.send("Invalid input. Please enter Male, Female, M,  F, NB, or NonBinary")
                        continue  # Repeat the loop if input is invalid
                    if user_gender == "m":
                        user_gender = "male"
                    elif user_gender == "f":
                        user_gender = "female"
                    elif user_gender == "nb" or user_gender == "nonbinary":
                        user_gender == "Non-Binary"
                        await ctx.send(f"Gender set to: {user_gender.capitalize()} ✅")
                        break
        
                    await ctx.send(f"Gender set to: {user_gender.capitalize()} ✅")
                    break  # Exit the loop if input is valid
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond! ❌")
                    return
            try:
                cursor.execute(
                    """
                    UPDATE Users
                    SET user_gender = %s
                    WHERE user_discord_id = %s
                    """,
                    (user_gender, member),
                )
                db.commit()
                await ctx.send("User data successfully saved to the database! ✅")
        
            except Exception as e:
                await ctx.send(f"An error occurred while saving your data: {e}")
        elif msg.content == "2":
            while True:
                await ctx.send(
                    "Please enter the number corresponding to your pronouns:\n"
                    "1️⃣ - He/Him\n"
                    "2️⃣ - She/Her\n"
                    "3️⃣ - He/They\n"
                    "4️⃣ - She/They\n"
                    "5️⃣ - They/Them"
                )
            
                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    pronoun_choices = {"1": "He/Him", "2": "She/Her", "3": "He/They", "4": "She/They", "5": "They/Them"}
                    
                    if msg.content not in pronoun_choices:
                        await ctx.send("Invalid input. Please enter 1, 2, 3, 4, or 5.")
                        continue
            
                    user_pronouns = pronoun_choices[msg.content]
                    await ctx.send(f"Pronouns set to: {user_pronouns} ✅")
                    break
            
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond! ❌")
                    return
            try:
                cursor.execute(
                    """
                    UPDATE Users
                    SET user_pronouns = %s
                    WHERE user_discord_id = %s
                    """,
                    (user_pronouns, member),
                )
                db.commit()
                await ctx.send("User data successfully saved to the database! ✅")
        
            except Exception as e:
                await ctx.send(f"An error occurred while saving your data: {e}")
        elif msg.content == "3":
            while True:
                await ctx.send("Please respond with your age!")
                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    if len(msg.content) > 2:
                        await ctx.send("Please enter a valid age.")
                        continue
                    user_age = msg.content
                    user_age = int(user_age)
                    await ctx.send(f"Set your age to {user_age}!")
                    break
            
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond! ❌")
                    return
            try:
                cursor.execute(
                    """
                    UPDATE Users
                    SET user_age = %s
                    WHERE user_discord_id = %s
                    """,
                    (user_age, member),
                )
                db.commit()
                await ctx.send("User data successfully saved to the database! ✅")
        
            except Exception as e:
                await ctx.send(f"An error occurred while saving your data: {e}")
        elif msg.content == "4":
            while True:
                await ctx.send("Please enter your date of birth in the format YYYY-MM-DD:")
                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
            
                    if not re.match(date_pattern, msg.content):
                        await ctx.send("Invalid format! Please enter your date of birth in YYYY-MM-DD format (e.g., 2000-05-15).")
                        continue
            
                    user_date_of_birth = msg.content
                    await ctx.send(f"Date of birth set to: {user_date_of_birth} ✅")
                    break
            
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond! ❌")
                    return
            try:
                cursor.execute(
                    """
                    UPDATE Users
                    SET user_date_of_birth = %s
                    WHERE user_discord_id = %s
                    """,
                    (user_date_of_birth, member),
                )
                db.commit()
                await ctx.send("User data successfully saved to the database! ✅")
        
            except Exception as e:
                await ctx.send(f"An error occurred while saving your data: {e}")
        elif msg.content == "5":
            while True:
                await ctx.send("Please enter a bio! (Max 255 characters)")
                try:
                    msg = await bot.wait_for("message", check=check, timeout=180)
                    if len(msg.content) > 255:
                        await ctx.send(f'HEY! <@{member}> I SAID ONLY 255 CHARACTERS MAX!!!')
                        continue
                    user_bio = str(msg.content)
                    await ctx.send("I added/updated your profiles BIO! Thanks!")
                    break
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond! ❌")
                    return
            try:
                cursor.execute(
                    """
                    UPDATE Users
                    SET user_bio = %s
                    WHERE user_discord_id = %s
                    """,
                    (user_bio, member),
                )
                db.commit()
                await ctx.send("User data successfully saved to the database! ✅")
        
            except Exception as e:
                await ctx.send(f"An error occurred while saving your data: {e}")
    except:
        await ctx.send("You didnt enter a correct value... Please try running the command again...")
        return

@bot.command()
async def aboutme(ctx):
    if ctx.channel.id != 1343127549861167135:
        await ctx.send(f"Please use <#1343127549861167135> and not <#{ctx.channel.id}>!")
    user_discord_id = ctx.author.id
    cursor.execute("SELECT 1 FROM Users WHERE user_discord_id = %s", (user_discord_id,))
    userCheck = cursor.fetchone()  # Fetch the first result
    if userCheck is None:
        await ctx.send(f'Hey <@{user_discord_id}>! You don\'t seem to have a profile. Please try making one using ?createuser')
        return

    name = ctx.author.nick
    if name == None:
        name = ctx.author.name
    
    # Fetching data for the profile
    cursor.execute("SELECT user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_bio, user_joined_at, user_created_at FROM Users WHERE user_discord_id = %s", (user_discord_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        await ctx.send(f'Hey <@{user_discord_id}>! We encountered an issue retrieving your profile information.')
        return
    
    user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_bio, user_joined_at, user_created_at = user_data
    
    # Prepare the embed
    aboutMeEmbed = nextcord.Embed(
        title=f"Get to know {name}!",
        description=f"{name}'s discord name is {user_name} and they were born on {user_date_of_birth}",
        color=0xff00ea
    )
    
    aboutMeEmbed.set_author(
        name=f"{name}'s About Me!",
        icon_url=str(ctx.author.avatar.url)
    )
    
    aboutMeEmbed.add_field(
        name=f"{name}'s Gender",
        value=f"{name} identifies as {user_gender}",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Pronouns",
        value=f"{name} uses {user_pronouns} pronouns",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Age",
        value=f"{name} is {user_age} years old",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s User Bio",
        value=user_bio or 'No bio set.',
        inline=False
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Server Join Date",
        value=f"{name} joined the server on {str(user_joined_at)[:10]}",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Account Creation",
        value=f"{name} created their account on {str(user_created_at)[:10]}",
        inline=True
    )
    
    # Send the embed
    await ctx.send(embed=aboutMeEmbed)

@bot.command()
async def whois(ctx, member: nextcord.Member = None):
    if member == None:
        await ctx.send(f"Please @ a member when using this command like this! ?whois {dripMention}")
        return
    if ctx.channel.id != 1343127549861167135:
        await ctx.send(f"Please use <#1343127549861167135> and not <#{ctx.channel.id}>!")
        return
    user_discord_id = member.id
    cursor.execute("SELECT 1 FROM Users WHERE user_discord_id = %s", (user_discord_id,))
    userCheck = cursor.fetchone()  # Fetch the first result
    if userCheck is None:
        await ctx.send(f'Hey <@{ctx.author.id}>, it doesnt seem like <@{member.id}> has a profile. Please have them make one using ?createuser')
        return

    name = member.display_name
    
    # Fetching data for the profile
    cursor.execute("SELECT user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_bio, user_joined_at, user_created_at FROM Users WHERE user_discord_id = %s", (user_discord_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        await ctx.send(f'Hey <@{user_discord_id}>! We encountered an issue retrieving your profile information.')
        return
    
    user_name, user_gender, user_pronouns, user_age, user_date_of_birth, user_bio, user_joined_at, user_created_at = user_data
    
    # Prepare the embed
    aboutMeEmbed = nextcord.Embed(
        title=f"Get to know {name}!",
        description=f"{name}'s discord name is {user_name} and they were born on {user_date_of_birth}",
        color=0xff00ea
    )
    
    aboutMeEmbed.set_author(
        name=f"{name}'s About Me!",
        icon_url=str(member.display_avatar)
    )
    
    aboutMeEmbed.add_field(
        name=f"{name}'s Gender",
        value=f"{name} identifies as {user_gender}",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Pronouns",
        value=f"{name} uses {user_pronouns} pronouns",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Age",
        value=f"{name} is {user_age} years old",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s User Bio",
        value=user_bio or 'No bio set.',
        inline=False
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Server Join Date",
        value=f"{name} joined the server on {str(user_joined_at)[:10]}",
        inline=True
    )
    aboutMeEmbed.add_field(
        name=f"{name}'s Account Creation",
        value=f"{name} created their account on {str(user_created_at)[:10]}",
        inline=True
    )
    
    # Send the embed
    await ctx.send(embed=aboutMeEmbed)

@bot.command()
@commands.check(is_owner)
async def add_dob(ctx, member: nextcord.Member = None, dob: str = None):
    if member == None: # If member wasnt mentioned, dont continue command
        await ctx.send("Please mention a user in order to use this command!")
        return
    if dob == None: # If dob wasnt mentioned, dont continue command
        await ctx.send("Please enter a DOB in this format: YYYY-MM-DD")
        return
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        await ctx.send("Invalid date format! Please use YYYY-MM-DD.")
        return
    user_id = member.id
    user_dob = dob_date
    try:
        cursor.execute(
            """
            INSERT INTO HardCodedDOBs (user_id, user_dob)
            VALUES (%s, %s)
            """,
            (user_id, user_dob),
        )
        db.commit()
        await ctx.send("User data successfully saved to the database! ✅")
    except Exception as e:
        await ctx.send(f"An error occurred while saving your data: {e}")

@bot.command()
@commands.check(is_owner)
async def sql(ctx, *, query: str = None):
    if query == None:
        await ctx.send("Please input a query you want to run.")
        return
    try: 
        cursor.execute(f'{query};')
        if 'select' in query.lower():
            selected_data = cursor.fetchall()
            formatted_data = "\n".join([str(row) for row in selected_data])
            await ctx.send(f"**Query Results:**\n{formatted_data}")
            return
        else:
            db.commit()
            await ctx.send(f"Succesfully ran: ```\n{query}\n```")
    except Exception as e:
        # Catch any other unexpected errors
        await ctx.send(f"An unexpected error occurred: {str(e)}")


@bot.command()
async def praise(ctx, member: nextcord.Member = None):
    if member is None:
      await ctx.send("Please ping the user you wish to praise!")
    else:
      message_type = random.randint(1, 10)
      messages = {
              1: f"{member.mention}, you look so good right now.",
              2: f"{member.mention}, I love you.",
              3: f"{member.mention}, you deserve a gold star.",
              4: f"{member.mention}, youre quite the gem, a lovely one at that.",
              5: f"{member.mention}, you always brighten my day.",
              6: f"{member.mention}, good job kitten.",
              7: f"womp womp {member.mention}, no praise for you :(",
              8: f"{member.mention}, you can be my skibidi rizzler.",
              9: f"{member.mention}, I would choose you in a garden of roses.",
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
        deleted = await ctx.channel.purge(limit=amount + 1)
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

@bot.command()
@commands.check(is_owner)
async def restart(ctx):
    if str(ctx.author.id) != dripID:
        for i in range(1, 5, 1):
            await ctx.send(f'{dripMention}!!! <@{ctx.author.id}> IS TRYING TO RESTART THE BOT WITHOUT YOUR PERMISSION!!! GET THEM!!!')
            time.sleep(0.1)
        return
        
    close_message = await ctx.send("Restarting Bot, Please wait")
    for i in range(1, 3, 1):
        dots = "." * i
        await close_message.edit(content=f"{close_message}{dots}")
    await bot.close()

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

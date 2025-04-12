import discord
import os
import json
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

# Developed by Aaron N + ChatGPT; 3/23/25
TOKEN = os.getenv("DISCORD_TOKEN")  # Store token in Replit secrets

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

client = discord.Client(intents=intents)


@bot.tree.command(name="hello", description="Say hello to the bot")
async def first_command(interaction):
    await interaction.response.send_message("Hello!")


# Role Name Format
GRADE_ROLE_FORMAT = "[{}]"
ALUMNI_ROLE_NAME = "[ALUMNI]"

# Scheduler setup
scheduler = AsyncIOScheduler()


def save_schedule(month, day):
    schedule_data = {"month": month, "day": day}
    with open("schedule.json", "w") as f:
        json.dump(schedule_data, f)


def load_schedule():
    try:
        with open("schedule.json", "r") as f:
            schedule_data = json.load(f)
            month, day = schedule_data["month"], schedule_data["day"]
            scheduler.add_job(lambda: increment_all_grades(bot.guilds[0]),
                              'date',
                              run_date=datetime(datetime.now().year, month,
                                                day))
            print(f"Loaded scheduled update for {month}/{day}")
    except (FileNotFoundError, json.JSONDecodeError):
        print("No previous schedule found.")


async def get_grade_roles(guild):
    grade_roles = {}
    for role in guild.roles:
        if role.name == ALUMNI_ROLE_NAME:
            grade_roles["ALUMNI"] = role.id
        elif role.name.startswith("[") and role.name.endswith("]"):
            try:
                grade = int(role.name[1:-1])
                grade_roles[grade] = role.id
            except ValueError:
                pass  # Ignore roles that don't fit the format
    return grade_roles


async def increment_all_grades(guild):
    grade_roles = await get_grade_roles(guild)
    for member in guild.members:
        for grade, role_id in grade_roles.items():
            role = discord.utils.get(guild.roles, id=role_id)
            if role in member.roles:
                await increment_grade(member, guild, role_id, grade_roles)
                break


async def decrement_all_grades(guild):
    grade_roles = await get_grade_roles(guild)
    for member in guild.members:
        for grade, role_id in grade_roles.items():
            role = discord.utils.get(guild.roles, id=role_id)
            if role in member.roles:
                await decrement_grade(member, guild, role_id, grade_roles)
                break


def schedule_annual_update():
    scheduler.add_job(lambda: increment_all_grades(bot.guilds[0]),
                      'date',
                      run_date=datetime(datetime.now().year, 8, 1))
    scheduler.start()


async def increment_grade(member, guild, current_role_id, grade_roles):
    current_grade = next(
        (g for g, rid in grade_roles.items() if rid == current_role_id), None)

    if current_grade is None:
        try:
            await member.send("Error: Could not determine your grade level.")
        except discord.HTTPException:
            print(f"Could not DM {member.name}.")
        return

    if current_grade == "ALUMNI":
        print(f"{member.name} is already an Alumni.")
        return  # Exit the function early

    next_grade = current_grade + 1 if isinstance(current_grade,
                                                 int) else "ALUMNI"
    new_role_id = grade_roles.get(next_grade)

    old_role = discord.utils.get(guild.roles, id=current_role_id)
    new_role = discord.utils.get(guild.roles, id=new_role_id)

    if old_role:
        await member.remove_roles(old_role)
    if new_role:
        await member.add_roles(new_role)

    try:
        await member.send(f"Your grade has been updated to {next_grade}.")
    except discord.HTTPException:
        print(f"Could not DM {member.name}, but grade was updated.")


async def decrement_grade(member, guild, current_role_id, grade_roles):
    current_grade = next(
        (g for g, rid in grade_roles.items() if rid == current_role_id), None)

    if current_grade is None:
        try:
            await member.send("Error: Could not determine your grade level.")
        except discord.HTTPException:
            print(f"Could not DM {member.name}.")
        return

    if isinstance(
            current_grade,
            int) and current_grade == 9:  # Prevent demotion below 9th grade
        print(f"{member.name} is already in 9th grade.")
        return

    previous_grade = current_grade - 1 if isinstance(current_grade,
                                                     int) else 12
    new_role_id = grade_roles.get(previous_grade)

    old_role = discord.utils.get(guild.roles, id=current_role_id)
    new_role = discord.utils.get(guild.roles, id=new_role_id)

    if old_role:
        await member.remove_roles(old_role)
    if new_role:
        await member.add_roles(new_role)

    try:
        await member.send(f"Your grade has been updated to {previous_grade}.")
    except discord.HTTPException:
        print(f"Could not DM {member.name}, but grade was updated.")


@bot.command()
async def increment(ctx, member: discord.Member):
    grade_roles = await get_grade_roles(ctx.guild)
    for grade, role_id in grade_roles.items():
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        if role in member.roles:
            await increment_grade(member, ctx.guild, role_id, grade_roles)
            await ctx.send(f"{member.mention} has been promoted!")
            break


@bot.command()
async def decrement(ctx, member: discord.Member):
    grade_roles = await get_grade_roles(ctx.guild)
    for grade, role_id in grade_roles.items():
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        if role in member.roles:
            if isinstance(grade, int) and grade == 9:
                await ctx.send("Cannot demote below 9th grade.")
                return
            await member.remove_roles(role)
            previous_grade = grade - 1 if isinstance(grade, int) else 12
            new_role_id = grade_roles.get(previous_grade)
            if new_role_id:
                await member.add_roles(discord.Object(id=new_role_id))
                await ctx.send(f"{member.mention} has been demoted!")
            break


@bot.command()
async def schedule_update(ctx, month: int, day: int):
    save_schedule(month, day)  # Save to file
    scheduler.add_job(lambda: increment_all_grades(ctx.guild),
                      'date',
                      run_date=datetime(datetime.now().year, month, day))
    await ctx.send(f"Grade update scheduled for {month}/{day}!")


@bot.command()
async def reschedule_update(ctx, month: int, day: int):
    scheduler.remove_all_jobs()
    save_schedule(month, day)  # Save to file
    await schedule_update(ctx, month, day)
    await ctx.send(f"Grade update rescheduled for {month}/{day}!")


@bot.command()
async def cancel_update(ctx):
    scheduler.remove_all_jobs()  # Remove scheduled jobs
    try:
        os.remove("schedule.json")  # Delete the saved schedule file
    except FileNotFoundError:
        pass  # If the file doesn't exist, ignore the error

    await ctx.send("Scheduled grade update has been canceled.")


@bot.command()
async def check_schedule(ctx):
    try:
        with open("schedule.json", "r") as f:
            schedule_data = json.load(f)
            month, day = schedule_data["month"], schedule_data["day"]
            await ctx.send(f"Next scheduled grade update is on {month}/{day}.")
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("No scheduled grade update found.")


@bot.command()
async def increment_all(ctx):
    await increment_all_grades(ctx.guild)
    await ctx.send("All grades have been updated!")


@bot.command()
async def decrement_all(ctx):
    await decrement_all_grades(ctx.guild)
    await ctx.send("All grades have been reverted!")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    load_schedule()  # Load and restore schedule if it exists
    schedule_annual_update()  # Ensure annual update is scheduled
    await bot.tree.sync()


bot.run(TOKEN)

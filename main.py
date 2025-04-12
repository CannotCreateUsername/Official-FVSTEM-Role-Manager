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
bot = commands.Bot(command_prefix="~", intents=intents)

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
            await member.send(f"Error: Could not determine your grade level in {guild.name}.")
        except discord.HTTPException:
            print(f"Could not DM {member.name}.")
        return

    if current_grade == "ALUMNI":
        print(f"{member.name} is already an Alumni in {guild.name}.")
        return  # Exit the function early

    next_grade = current_grade + 1 if isinstance(current_grade, int) else "ALUMNI"
    new_role_id = grade_roles.get(next_grade)

    # Corrected logic to handle the transition to Alumni
    if current_grade == 12:
        new_grade = "ALUMNI"
        new_role_id = grade_roles.get("ALUMNI")
    else:
        new_grade = next_grade

    old_role = discord.utils.get(guild.roles, id=current_role_id)
    new_role = discord.utils.get(guild.roles, id=new_role_id)

    if old_role:
        await member.remove_roles(old_role)
    if new_role:
        await member.add_roles(new_role)

    try:
        await member.send(f"Your grade has been updated to **[{new_grade}]** in **{guild.name}**.")
    except discord.HTTPException:
        print(f"Could not DM {member.name}, but grade was updated in {guild.name}.")


async def decrement_grade(member, guild, current_role_id, grade_roles):
    current_grade = next(
        (g for g, rid in grade_roles.items() if rid == current_role_id), None)

    if current_grade is None:
        try:
            await member.send(f"Error: Could not determine your grade level in {guild.name}.")
        except discord.HTTPException:
            print(f"Could not DM {member.name}.")
        return

    if isinstance(current_grade, int) and current_grade == 9:  # Prevent demotion below 9th grade
        print(f"{member.name} is already in 9th grade in {guild.name}.")
        return

    previous_grade = current_grade - 1 if isinstance(current_grade, int) else 12
    new_role_id = grade_roles.get(previous_grade)

    old_role = discord.utils.get(guild.roles, id=current_role_id)
    new_role = discord.utils.get(guild.roles, id=new_role_id)

    if old_role:
        await member.remove_roles(old_role)
    if new_role:
        await member.add_roles(new_role)

    try:
        await member.send(f"Your grade has been updated to **[{previous_grade}]** in **{guild.name}**.")
    except discord.HTTPException:
        print(f"Could not DM {member.name}, but grade was updated in {guild.name}.")


@bot.tree.command(name="increment", description="Promote a member's grade")
async def increment_slash(interaction: discord.Interaction, member: discord.Member):
    grade_roles = await get_grade_roles(interaction.guild)
    for grade, role_id in grade_roles.items():
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role in member.roles:
            await increment_grade(member, interaction.guild, role_id, grade_roles)
            await interaction.response.send_message(f"{member.mention} has been promoted!")
            return
    await interaction.response.send_message("Could not find a valid grade role for this member.")


@bot.tree.command(name="decrement", description="Demote a member's grade")
async def decrement_slash(interaction: discord.Interaction, member: discord.Member):
    grade_roles = await get_grade_roles(interaction.guild)
    found_role = False
    for grade, role_id in grade_roles.items():
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role in member.roles:
            await decrement_grade(member, interaction.guild, role_id, grade_roles)
            await interaction.response.send_message(f"{member.mention} has been demoted!")
            found_role = True
            break
    if not found_role:
        await interaction.response.send_message("Could not find a valid grade role for this member.")


@bot.tree.command(name="schedule_update", description="Schedule an annual grade update")
async def schedule_update_slash(interaction: discord.Interaction, month: int, day: int):
    save_schedule(month, day)  # Save to file
    scheduler.add_job(lambda: increment_all_grades(interaction.guild),
                      'date',
                      run_date=datetime(datetime.now().year, month, day))
    await interaction.response.send_message(f"Grade update scheduled for {month}/{day}!")


@bot.tree.command(name="reschedule_update", description="Reschedule the annual grade update")
async def reschedule_update_slash(interaction: discord.Interaction, month: int, day: int):
    scheduler.remove_all_jobs()
    save_schedule(month, day)  # Save to file
    scheduler.add_job(lambda: increment_all_grades(interaction.guild),
                        'date',
                        run_date=datetime(datetime.now().year, month, day))
    await interaction.response.send_message(f"Grade update rescheduled for {month}/{day}!")


@bot.tree.command(name="cancel_update", description="Cancel the scheduled grade update")
async def cancel_update_slash(interaction: discord.Interaction):
    scheduler.remove_all_jobs()  # Remove scheduled jobs
    try:
        os.remove("schedule.json")  # Delete the saved schedule file
    except FileNotFoundError:
        pass  # If the file doesn't exist, ignore the error

    await interaction.response.send_message("Scheduled grade update has been canceled.")


@bot.tree.command(name="check_schedule", description="Check the date of the scheduled grade update")
async def check_schedule_slash(interaction: discord.Interaction):
    try:
        with open("schedule.json", "r") as f:
            schedule_data = json.load(f)
            month, day = schedule_data["month"], schedule_data["day"]
            await interaction.response.send_message(f"Next scheduled grade update is on {month}/{day}.")
    except (FileNotFoundError, json.JSONDecodeError):
        await interaction.response.send_message("No scheduled grade update found.")


@bot.tree.command(name="increment_all", description="Increment the grade for all members")
async def increment_all_slash(interaction: discord.Interaction):
    await increment_all_grades(interaction.guild)
    await interaction.response.send_message("All grades have been updated!")


@bot.tree.command(name="decrement_all", description="Decrement the grade for all members")
async def decrement_all_slash(interaction: discord.Interaction):
    await decrement_all_grades(interaction.guild)
    await interaction.response.send_message("All grades have been reverted!")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    load_schedule()  # Load and restore schedule if it exists
    schedule_annual_update()  # Ensure annual update is scheduled
    await bot.tree.sync()

bot.run(TOKEN)
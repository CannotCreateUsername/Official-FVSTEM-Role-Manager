# Discord Grade Management Bot

This Discord bot automates the management of grade-based roles within your server. It allows for manual promotion and demotion of members, as well as scheduled annual grade updates. The bot identifies grade roles based on a specific naming convention.

## Features

* **Slash Commands:** Utilizes Discord's modern slash command interface for easy interaction.
* **Role-Based Grade System:** Automatically identifies grade roles based on the names `[9]`, `[10]`, `[11]`, `[12]`, and `[ALUMNI]`.
* **Manual Promotion (`/increment`):** Promotes a selected member to the next grade role. Members in the "[12]" role are moved to the "[ALUMNI]" role.
* **Manual Demotion (`/decrement`):** Demotes a selected member to the previous grade role. Prevents demotion below the "[9]" role.
* **Scheduled Annual Update (`/schedule_update`):** Schedules an automatic promotion of all members with grade roles on a specified date (month/day).
* **Reschedule Update (`/reschedule_update`):** Changes the date of the scheduled annual grade update.
* **Cancel Update (`/cancel_update`):** Cancels any previously scheduled annual grade update.
* **Check Schedule (`/check_schedule`):** Displays the date of the next scheduled grade update.
* **Increment All (`/increment_all`):** Immediately promotes all members with grade roles.
* **Decrement All (`/decrement_all`):** Immediately demotes all members with grade roles.
* **Direct Messages (DMs):** Sends users a DM when their grade role is updated, indicating the new grade and the server where the update occurred.
* **Alumni Handling:** Properly transitions members from 12th grade to the Alumni role.
* **Error Handling:** Provides informative messages in case of errors (e.g., no grade role found, cannot demote below 9th grade).

## Setup

1.  **Create a Discord Bot:**
    * Go to the [Discord Developer Portal](https://discord.com/developers/applications).
    * Create a new application.
    * Navigate to the "Bot" tab and click "Add Bot".
    * Enable "Server Members Intent" and "Message Content Intent" under "Privileged Gateway Intents".
    * Copy the bot's token.

2.  **Invite the Bot to Your Server:**
    * In the Developer Portal, go to the "OAuth2" tab, then "URL Generator".
    * Select the "bot" scope and the "applications.commands" scope.
    * Choose the necessary permissions (at a minimum, "Manage Roles").
    * Copy the generated URL and paste it into your web browser to invite the bot to your server.

3.  **Set Up Environment Variables:**
    * This bot uses the `DISCORD_TOKEN` environment variable to store your bot's token securely.
    * If you are using a service like Replit, add `DISCORD_TOKEN` as a secret.
    * If running locally, you can set it in your terminal or a `.env` file (you'll need to install the `python-dotenv` library).

4.  **Install Dependencies:**
    ```bash
    pip install discord.py apscheduler
    ```

5.  **Run the Bot:**
    ```bash
    python your_bot_file_name.py
    ```
    (Replace `your_bot_file_name.py` with the actual name of your Python file).

6.  **Create Grade Roles:**
    * In your Discord server settings, create roles named exactly `[9]`, `[10]`, `[11]`, `[12]`, and `[ALUMNI]`. The bot relies on these specific names to identify and manage the grade levels.

## Usage

Once the bot is running and invited to your server, you can use the following slash commands:

* `/hello`: The bot will say hello! (A basic test command).
* `/increment <member>`: Promotes the mentioned member to the next grade role.
* `/decrement <member>`: Demotes the mentioned member to the previous grade role.
* `/schedule_update <month> <day>`: Schedules the annual grade update for the specified month and day (e.g., `/schedule_update 8 1` for August 1st).
* `/reschedule_update <month> <day>`: Changes the scheduled annual grade update to the new month and day.
* `/cancel_update`: Cancels the currently scheduled annual grade update.
* `/check_schedule`: Displays the date of the next scheduled grade update, if any.
* `/increment_all`: Immediately promotes all members who have one of the defined grade roles.
* `/decrement_all`: Immediately demotes all members who have one of the defined grade roles.

## Important Notes

* The bot relies heavily on the correct naming of the grade roles (`[9]`, `[10]`, `[11]`, `[12]`, `[ALUMNI]`). Ensure these roles exist and are named exactly as specified.
* The bot needs the "Manage Roles" permission to add and remove roles from members.
* The "Server Members Intent" and "Message Content Intent" are required for the bot to access the necessary member information. Make sure these are enabled in the Discord Developer Portal.
* The annual update is scheduled based on the server's time.

## Contributing

Contributions to this bot are welcome! Feel free to fork the repository and submit pull requests with improvements or bug fixes.

## Developed By

Aaron N + ChatGPT + Gemini (4/12/25)
import logging
import json
import os

# Log file path at project root
LOG_FILE = os.path.abspath(os.path.join(os.getcwd(), "bot_logs.json"))

# Ensure the log file starts as a valid JSON object if empty
if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

class CustomJSONFormatter(logging.Formatter):
    """Formats logs as a JSON dictionary with timestamp as the key."""

    def format(self, record):
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        # Fetch user-related information if available
        user_info = getattr(record, "user_info", None)

        # Default user information
        user_input = user_info if user_info else "NONE"

        log_entry = {
            "level": record.levelname,
            "message": record.getMessage(),
            "user": user_input,  # Include user info here
            "name": record.name,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps({timestamp: log_entry}, ensure_ascii=False)

class JSONFileHandler(logging.FileHandler):
    """Custom handler to store logs as a JSON dictionary."""

    def emit(self, record):
        log_entry = json.loads(self.format(record))  # Convert formatted string to dict
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            try:
                logs = json.load(f)  # Load existing logs
            except json.JSONDecodeError:
                logs = {}

            logs.update(log_entry)  # Merge new log
            f.seek(0)
            json.dump(logs, f, ensure_ascii=False, indent=4)

# Logger setup
logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

handler = JSONFileHandler(LOG_FILE, mode="a", encoding="utf-8")
handler.setFormatter(CustomJSONFormatter())

logger.addHandler(handler)

# Example command logging function
def log_command(ctx, command_name):
    """Log a command executed by the user with their username and ID."""
    
    # Gather user-related info from the context (ctx)
    user_info = {
        "id": str(ctx.author.id),
        "username": ctx.author.username,  # Corrected this line
        "bot": str(ctx.author.bot),
        "nick": ctx.author.nick if ctx.author.nick else None,
        "premium_since": str(ctx.author.premium_since) if ctx.author.premium_since else None,
        "communication_disabled_until": str(ctx.author.communication_disabled_until) if ctx.author.communication_disabled_until else None,
        "_guild_id": str(ctx.guild.id) if ctx.guild else None,
        "user_ref": "Missing"  # Add additional reference if necessary (optional field)
    }
    
    # Log the command execution with the gathered user info
    logger.info(f"Command '{command_name}' executed.", extra={"user_info": user_info})

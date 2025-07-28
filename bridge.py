# bridge.py

from queue import Queue
from threading import Lock

# 🧠 Bot activation flag + lock
bot_active = True
bot_state_lock = Lock()

def activate_bot():
    global bot_active
    with bot_state_lock:
        bot_active = True

def deactivate_bot():
    global bot_active
    with bot_state_lock:
        bot_active = False

def is_bot_active():
    with bot_state_lock:
        return bot_active

# 🔒 Shared Lock for API access
api_lock = Lock()

# Boss puts commands here, API takes them
commands_queue = Queue()

# API puts results here, Boss reads them
results_queue = Queue()

# Direct replies for commands
reply_queue = Queue()
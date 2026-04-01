from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio
import os

app = Flask(__name__)

# Azure credentials (from Environment Variables)
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Adapter setup
settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)


# Error handler
async def on_error(context: TurnContext, error: Exception):
    await context.send_activity("Error occurred!")
    print(error)

adapter.on_turn_error = on_error


# Bot logic
async def handle_message(turn_context: TurnContext):
    user_msg = turn_context.activity.text.lower()

    if "hello" in user_msg:
        reply = "Hello 👋 I am your AI Shopping Bot!"
    elif "product" in user_msg:
        reply = "We have: laptop, phone, watch"
    elif "price" in user_msg:
        reply = "Laptop ₹60,000 | Phone ₹20,000"
    else:
        reply = f"You said: {user_msg}"

    await turn_context.send_activity(reply)


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_bot_logic(turn_context):
        await handle_message(turn_context)

    task = asyncio.run(adapter.process_activity(activity, auth_header, call_bot_logic))
    return Response(status=201)


@app.route("/")
def home():
    return "Azure Bot is Running ✅"


if __name__ == "__main__":
    app.run()
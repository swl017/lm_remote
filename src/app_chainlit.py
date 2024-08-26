import chainlit as cl
from openai import AsyncOpenAI

# Configure the async OpenAI client
client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

settings = {
    "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "temperature": 0.6,
    "max_tokens": -1,
    "max_tokens": 131072,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

@cl.on_chat_start
def start_chat():
    # Initialize message history
    cl.user_session.set("message_history", [{"role": "system", "content": "You are a helpful chatbot.  You help the user with the best of your effort."}])

@cl.on_message
async def main(message: cl.Message):
    # Retrieve the message history from the session
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    # Create an initial empty message to send back to the user
    msg = cl.Message(content="")
    await msg.send()

    # Use streaming to handle partial responses
    stream = await client.chat.completions.create(messages=message_history, stream=True, **settings)

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    # Append the assistant's last response to the history
    message_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("message_history", message_history)

    # Update the message after streaming completion
    await msg.update()


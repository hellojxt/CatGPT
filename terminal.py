import os
import platform

system = platform.system()
import openai
import tiktoken
from rich.console import Console
from rich.markdown import Markdown
console = Console()

openai.api_key = os.environ["OPENAI_API_KEY"]
messages=[
        {"role": "system", "content": "You are a helpful assistant."},
]
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_msg(msg) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = 0
    for message in msg:
        string = message["content"]
        num_tokens += len(encoding.encode(string))
    return num_tokens

while True:
    # with terminal colors
    text_in = input("\033[1;32mYou:\033[0m\n")
    messages.append({"role": "user", "content": text_in})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
        )
    print("\n\033[1;34mAssistant:\033[0m  ")
    content = ""
    for chunk in completion:
        if "content" in chunk["choices"][0]["delta"]:
            console.print(chunk["choices"][0]["delta"]["content"], end="")
            content += chunk["choices"][0]["delta"]["content"]
    messages.append({"role": "assistant", "content": content})
    token_num = num_tokens_from_msg(messages)
    print("\ntokens: ", token_num, " | cost: ", token_num / 1000 * 0.002, "$")
    print("\n")
    
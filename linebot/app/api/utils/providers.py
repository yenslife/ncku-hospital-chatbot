from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=OPENAI_API_KEY,
)
async_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)


def openai_api(messages, model="gpt-4.1-mini"):
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.5
    )

    return response.choices[0].message.content


# end def
if __name__ == "__main__":
    print(openai_api([{"role": "user", "content": "你知道王建民嗎？"}]))

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

model = "gpt-4.1-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def openai_api(messages):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.5
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print(openai_api([{"role": "user", "content": "你知道王建民嗎？"}]))

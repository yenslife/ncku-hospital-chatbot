from linebot.v3.messaging import AsyncMessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookParser
from dotenv import load_dotenv
import os

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 初始化 LINE Bot API 和 WebhookParser
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = AsyncMessagingApi(api_client)
webhook_parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

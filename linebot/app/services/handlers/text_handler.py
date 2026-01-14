"""處理文字訊息的模組"""

import json
import random

from linebot.models import TextSendMessage, FlexSendMessage

from app.services.handlers.common import create_quick_reply, COMMANDS
from app.api.dify import inference
from app.config.line_config import line_bot_api
from app.config.logger import get_logger
from app.services.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)
rate_limiter = RateLimiter(max_requests=50, window_seconds=3600)


def handle_text_message(event):
    """處理文字訊息"""
    try:
        user_input = event.message.text
        user_id = event.source.user_id
        user_profile = line_bot_api.get_profile(user_id)
        user_display_name = user_profile.display_name

        # 產生回應訊息
        quick_reply = None
        if user_input in COMMANDS:
            response_text = COMMANDS[user_input]
            if isinstance(response_text, list):  # 處理 /hint 指令的多個提示
                response_text = random.choice(response_text)
            quick_reply = create_quick_reply()
            return [TextSendMessage(text=response_text, quick_reply=quick_reply)]

        # 檢查使用次數，決定要不要 inference
        if not rate_limiter.is_allowed(user_id):
            remaining_time = rate_limiter.time_to_reset(user_id)
            minutes, seconds = divmod(remaining_time, 60)
            response_text_list = [
                f"我知道{user_display_name}很喜歡跟我聊天，不過我已經有點累了，請稍等 {minutes} 分 {seconds} 秒再來找我吧！",
                f"嗨，超過使用次數了，請稍等 {minutes} 分 {seconds} 秒再來找我吧！",
            ]
            response_text = (
                random.choice(response_text_list)
                if user_display_name
                else response_text_list[0]
            )
            return [
                TextSendMessage(text=response_text, quick_reply=create_quick_reply())
            ]

        # 處理一般查詢
        response_text = inference(user_input, user_id)
        quick_reply = create_quick_reply()

        # 處理可能包含 Flex Message 的回應，來自 Dify
        if "===FLEX_MESSAGE===" in response_text:
            parts = response_text.split("===FLEX_MESSAGE===")
            text_content = parts[0].strip()
            text_message = TextSendMessage(text=text_content, quick_reply=quick_reply)

            # 檢查是否有 Flex Message 部分
            if len(parts) > 1:
                flex_content = parts[1].strip().replace("```", "").replace("json", "")
                if flex_content and flex_content != "False":
                    try:
                        flex_json = json.loads(flex_content)
                        return [
                            text_message,
                            FlexSendMessage(alt_text="詳細資訊", contents=flex_json),
                        ]
                    except Exception as e:
                        logger.error(f"Flex訊息解析錯誤: {str(e)}", exc_info=True)

            return [text_message]

        # 純文字回應
        return [TextSendMessage(text=response_text, quick_reply=quick_reply)]

    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {str(e)}", exc_info=True)
        return [
            TextSendMessage(
                text="抱歉，系統發生錯誤，請稍後再試。",
                quick_reply=create_quick_reply(),
            )
        ]

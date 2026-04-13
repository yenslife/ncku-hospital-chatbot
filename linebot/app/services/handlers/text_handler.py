"""處理文字訊息的模組"""

import json
import random

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer

from app.services.handlers.common import (
    create_quick_reply,
    COMMANDS,
    send_message,
    show_loading_animation,
)
from app.api.dify import inference
from app.config.line_config import line_bot_api
from app.config.logger import get_logger
from app.services.utils.rate_limiter import RateLimiter
from app.services.utils.flex_message import flex_message_convert_to_json
from app.repositories.user_repository import UserRepository
from app.db.database import SessionLocal

logger = get_logger(__name__)
rate_limiter = RateLimiter(max_requests=50, window_seconds=3600)


async def handle_text_message(event):
    """處理文字訊息"""
    try:
        user_input = event.message.text
        user_id = event.source.user_id
        user_profile = line_bot_api.get_profile(user_id)
        user_display_name = user_profile.display_name

        quick_reply = None
        if user_input in COMMANDS:
            # 特殊處理：基本資料 flex message
            if user_input == "/基本資料":
                db = SessionLocal()
                try:
                    user_repository = UserRepository(db)
                    user_data = user_repository.get_user(user_id)

                    # 載入 flex message template
                    flex_json = flex_message_convert_to_json(
                        "flex_messages/基本資料.json"
                    )

                    # 替換佔位符
                    flex_str = json.dumps(flex_json, ensure_ascii=False)
                    flex_str = flex_str.replace(
                        "===BED_NO===", user_data.bed_number or "尚未設定"
                    )
                    flex_str = flex_str.replace(
                        "===DIAGNOSIS===", user_data.diagnosis or "尚未設定"
                    )
                    flex_str = flex_str.replace(
                        "===DOCTOR===", user_data.attending_physician or "尚未設定"
                    )
                    flex_json = json.loads(flex_str)

                    flex_message = FlexMessage(
                        alt_text="基本資料", contents=FlexContainer.from_dict(flex_json)
                    )
                    await send_message(event.reply_token, [flex_message])
                    return
                finally:
                    db.close()

            # 特殊處理：洗腎原因
            if user_input == "/洗腎原因":
                db = SessionLocal()
                try:
                    user_repository = UserRepository(db)
                    user_data = user_repository.get_user(user_id)

                    dialysis_reason = user_data.dialysis_reason or "尚未設定洗腎原因"
                    await send_message(
                        event.reply_token,
                        [
                            TextMessage(
                                text=f"洗腎原因：{dialysis_reason}",
                                quick_reply=create_quick_reply(),
                            )
                        ],
                    )
                    return
                finally:
                    db.close()

            response_text = COMMANDS[user_input]
            if isinstance(response_text, list):
                response_text = random.choice(response_text)
            quick_reply = create_quick_reply()
            await send_message(
                event.reply_token,
                [TextMessage(text=response_text, quick_reply=quick_reply)],
            )
            return

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
            await send_message(
                event.reply_token,
                [TextMessage(text=response_text, quick_reply=create_quick_reply())],
            )
            return

        await show_loading_animation(user_id)
        response_text = await inference(user_input, user_id)
        if user_input == "有什麼東西不能吃？":
            quick_reply = create_quick_reply(
                [("醫院餐點", "醫院餐點"), ("家屬自備", "家屬自備")]
            )
        else:
            quick_reply = create_quick_reply()

        # 處理可能包含 Flex Message 的回應，來自 Dify
        if "===FLEX_MESSAGE===" in response_text:
            parts = response_text.split("===FLEX_MESSAGE===")
            text_content = parts[0].strip()
            text_message = TextMessage(text=text_content, quick_reply=quick_reply)

            if len(parts) > 1:
                flex_content = parts[1].strip().replace("```", "").replace("json", "")
                if flex_content and flex_content != "False":
                    try:
                        flex_json = json.loads(flex_content)
                        await send_message(
                            event.reply_token,
                            [
                                text_message,
                                FlexMessage(alt_text="詳細資訊", contents=flex_json),
                            ],
                        )
                        return
                    except Exception as e:
                        logger.error(f"Flex訊息解析錯誤: {str(e)}", exc_info=True)

            await send_message(event.reply_token, [text_message])
            return

        await send_message(
            event.reply_token,
            [TextMessage(text=response_text, quick_reply=quick_reply)],
        )

    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {str(e)}", exc_info=True)
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="抱歉，系統發生錯誤，請稍後再試。",
                    quick_reply=create_quick_reply(),
                )
            ],
        )

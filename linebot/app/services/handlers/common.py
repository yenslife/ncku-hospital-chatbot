"""共用函式模組"""

import json
import httpx
from linebot.v3.messaging import (
    QuickReply,
    QuickReplyItem,
    MessageAction,
    ReplyMessageRequest,
)
from app.config.line_config import line_bot_api, LINE_CHANNEL_ACCESS_TOKEN
from app.config.logger import get_logger

logger = get_logger(__name__)

COMMANDS = {
    "/hint": [
        "你可以試試看點擊下方的按鈕！",
        "嗨，你知道可以用錄音的方式來和我互動嗎？如果你不想打字可以直接錄音跟我說喔！",
    ],
    "🚧 尚未施工完畢，敬請期待！ 🚧": "🚧 尚未施工完畢，敬請期待！ 🚧",  # for future use
}


def create_quick_reply() -> QuickReply:
    """建立快速回覆按鈕"""
    return QuickReply(
        items=[
            QuickReplyItem(action=MessageAction(label="小提示 💡", text="/hint")),
        ]
    )


async def show_loading_animation(user_id: str, duration: int = 60) -> bool:
    """顯示 LINE Bot loading 動畫"""
    try:
        url = "https://api.line.me/v2/bot/chat/loading/start"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        }
        data = {
            "chatId": user_id,
            "loadingSeconds": min(max(duration, 5), 60),
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 202:
                logger.info(
                    f"已顯示 loading 動畫 (user_id: {user_id}, duration: {duration})"
                )
                return True
            else:
                logger.error(
                    f"顯示 loading 動畫失敗: {response.status_code} - {response.text}"
                )
                return False
    except Exception as e:
        logger.error(f"顯示 loading 動畫時發生錯誤: {str(e)}")
        return False


async def send_message(reply_token: str, messages: list) -> None:
    """發送訊息到 LINE"""
    try:
        readable_messages = json.dumps(
            [
                msg.as_json_dict() if hasattr(msg, "as_json_dict") else str(msg)
                for msg in messages
            ],
            ensure_ascii=False,
            indent=2,
        )
        logger.info(f"準備發送訊息 (可讀格式): {readable_messages}")
    except Exception as e:
        logger.warning(f"訊息轉換成 JSON 時發生錯誤: {e}")
        readable_messages = str(messages)

    flet_messages = []
    for msg in messages:
        flet_messages.extend(msg)

    logger.info(f"發送訊息: {flet_messages}")
    try:
        reply_request = ReplyMessageRequest(
            reply_token=reply_token, messages=flet_messages
        )
        line_bot_api.reply_message(reply_request)
    except Exception as e:
        logger.error(f"發送訊息時發生錯誤: {e}")
        raise
    logger.info(f"已發送訊息: {flet_messages}")

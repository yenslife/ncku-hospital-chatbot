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
from app.services.utils.flex_message import flex_message_convert_to_json

logger = get_logger(__name__)

COMMANDS = {
    "/hint": [
        "你可以試試看點擊下方的按鈕！",
        "嗨，你知道可以用錄音的方式來和我互動嗎？如果你不想打字可以直接錄音跟我說喔！",
    ],
    "/基本資料": ["成功點擊基本資料！"],
    "/常見問題": ["成功點擊常見問題！"],
    # "/知識寶典": [flex_message_convert_to_json("flex_messages/知識寶典.json")],
    "/知識寶典": ["成功點擊知識寶典！"],
    "/治療訊息": ["成功點擊治療訊息！"],
    "/專家線上療": ["成功點擊專家線上療！"],
    "/協助資源": ["成功點擊協助資源！"],
    "🚧 尚未施工完畢，敬請期待！ 🚧": "🚧 尚未施工完畢，敬請期待！ 🚧",  # for future use
}


def create_quick_reply(
    query_list: list[str] = [
        ("是不是要洗腎一輩子？", "是不是要洗腎一輩子？"),
        ("有什麼東西不能吃？", "有什麼東西不能吃？"),
        ("洗腎的時候血壓還好嗎？", "洗腎的時候血壓還好嗎？"),
        ("小提示 💡", "/hint"),
    ],
) -> QuickReply:
    """建立快速回覆按鈕"""
    items = []
    for query in query_list:
        items.append(
            QuickReplyItem(action=MessageAction(label=query[0], text=query[1]))
        )
    return QuickReply(items=items)


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

    logger.info(f"發送訊息: {messages}")
    try:
        reply_request = ReplyMessageRequest(
            # 注意 messages 最多只能五個
            reply_token=reply_token,
            messages=messages,
        )
        line_bot_api.reply_message(reply_request)
    except Exception as e:
        logger.error(f"發送訊息時發生錯誤: {e}")
        raise
    logger.info(f"已發送訊息: {messages}")

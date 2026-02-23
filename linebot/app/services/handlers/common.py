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
    
    ### Richmenu 的預設問題
    "/基本資料": ["成功點擊基本資料！"],
    "/常見問題": ["成功點擊常見問題！"],
    "/知識寶典": ["成功點擊知識寶典！"],
    "/治療訊息": ["成功點擊治療訊息！"],
    "/專家線上療": ["成功點擊專家線上療！"],
    "/協助資源": ["成功點擊協助資源！"],
    "🚧 尚未施工完畢，敬請期待！ 🚧": "🚧 尚未施工完畢，敬請期待！ 🚧",  # for future use
    
    ### Richmenu 知識寶典 -> 洗腎迷思
    "/洗腎後很快就會死亡？": ["洗腎可在腎臟失去功能時，發揮代替的作用，減少立即生命危險，也避免病人病情惡化。臨床上確實有少數病人洗腎後，原本病情未能改善甚至變糟，真正原因是身體已經有很多共病，有較高機會產生嚴重的併發症，洗腎的效果也因此大打折扣；反之若身體沒有合併其他疾病，大部分病人可以長期洗腎數十年並維持生活品質，同時也較有機會接受腎臟移植，徹底脫離洗腎。"],
    "/吃西藥會加重腎臟負擔？": ["藥品要經過肝腎代謝，在醫師處方或藥師指示下，以合理的劑量和使用方式用藥，其實是安全的，但若病人濫用消炎止痛藥，或是食用來路不明、成分不清楚的偏方，長期下來確實會傷害腎臟。"],
    "/洗腎就不用限制飲食？": ["洗腎大約可替代正常腎臟的1成，只能降低毒素的累積，因此飲食還是要配合營養師的建議，依照個別狀況控制蛋白質以及含鉀食物的攝取量，避免體內製造過多毒素。"],
    "/洗腎後就無法工作、失去自由？": ["目前有兩種洗腎方式，病人可與醫師討論哪種方式最符合需求。如果要上班、不方便定時到院所洗腎的病人，可選擇「腹膜透析」，定時自行操作換藥水來洗腎，適合擁有較佳自我照顧能力的病人，操作得當就連出國也不是問題。"],
    "/洗腎會讓皮膚變黑？": ["腎臟功能不佳時，病人容易貧血，再加上毒素累積就可能讓臉色變得暗沉，又稱為「尿毒臉」，反而是未妥善治療的腎臟病人比較會發生。醫療上可透過補充合成的紅血球生成素改善貧血，加上藉由洗腎清除毒素，有助於改善皮膚暗沉。"],
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

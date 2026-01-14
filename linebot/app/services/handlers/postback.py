from linebot.v3.messaging import (
    TextMessage,
    FlexMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
)
from app.config.logger import get_logger
from app.config.line_config import line_bot_api
from app.services.utils import flex_message_convert_to_json
from app.repositories.user_repository import UserRepository
from app.services.handlers.common import create_quick_reply, send_message

logger = get_logger(__name__)


def create_example_question_quickreply(questions: list[str]):
    return QuickReply(
        items=[
            QuickReplyItem(action=MessageAction(label=question, text=f"{question}"))
            for question in questions
        ]
    )


async def handle_postback_event(event):
    data = event.postback.data
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_display_name = user_profile.display_name

    await show_loading_animation(user_id)

    if data == "dialysis_causes":
        logger.info(f"使用者點擊 {user_display_name} 的 {user_id} 的 {data} 按鈕")
        await send_message(event.reply_token, [
            TextMessage(text="點擊「洗腎原因」"),
        ])
    elif data == "dialysis_catheter":
        logger.info(f"使用者點擊 {user_display_name} 的 {user_id} 的 {data} 按鈕")
        await send_message(event.reply_token, [
            TextMessage(text="點擊「洗腎管路」"),
        ])
    elif data == "dialysis_costs":
        logger.info(f"使用者點擊 {user_display_name} 的 {user_id} 的 {data} 按鈕")
        await send_message(event.reply_token, [
            TextMessage(text="點擊「洗腎費用」"),
        ])
    else:
        logger.warning(f"未知的 postback data: {data} from user {user_id}")

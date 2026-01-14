from linebot.models import (
    TextSendMessage,
    FlexSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction,
)
from app.config.logger import get_logger
from app.config.line_config import line_bot_api
from app.services.utils import flex_message_convert_to_json
from app.repositories.user_repository import UserRepository
from app.services.handlers.common import create_quick_reply

logger = get_logger(__name__)
user_repository = UserRepository()


def create_example_question_quickreply(questions: list[str]):
    return QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label=question, text=f"{question}"))
            for question in questions
        ]
    )


def handle_postback_event(event):
    data = event.postback.data
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_display_name = user_profile.display_name
    if data == "dialysis_causes":
        logger.info(f"使用者點擊 {user_display_name} 的 {user_id} 的 {data} 按鈕")
        return [
            TextSendMessage(text="點擊「洗腎原因」"),
        ]
    elif data == "dialysis_catheter":
        logger.info(f"使用者點擊 {user_display_name} 的 {user_id} 的 {data} 按鈕")
        return [
            TextSendMessage(text="點擊「洗腎管路」"),
        ]
    elif data == "dialysis_costs":
        logger.info(f"使用者點擊 {user_display_name} 的 {user_id} 的 {data} 按鈕")
        return [
            TextSendMessage(text="點擊「洗腎費用」"),
        ]
    else:
        logger.warning(f"Unknown postback data: {data} from user {user_id}")
        return None

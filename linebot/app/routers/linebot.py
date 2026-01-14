from fastapi import APIRouter, Request, HTTPException
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    AudioMessageContent,
    FollowEvent,
    PostbackEvent,
)
from app.config.line_config import webhook_parser
from app.services.message_service import MessageService
from app.services.welcome_service import WelcomeService
from app.services.postback_service import PostbackService
from app.config.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/linebot", tags=["linebot"])

message_service = MessageService()
welcome_service = WelcomeService()
postback_service = PostbackService()


@router.post("/webhook")
async def line_webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        events = webhook_parser.parse(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessageContent):
                logger.info("收到文字訊息")
                await message_service.handle_text_message(event)
            elif isinstance(event.message, ImageMessageContent):
                logger.info("收到圖片訊息")
                await message_service.handle_image_message(event)
            elif isinstance(event.message, AudioMessageContent):
                logger.info("收到音訊訊息")
                await message_service.handle_audio_message(event)
        elif isinstance(event, FollowEvent):
            logger.info("收到加入好友事件")
            await welcome_service.send_welcome_message(event)
        elif isinstance(event, PostbackEvent):
            logger.info("收到 Postback 事件")
            await postback_service.handle_postback_event(event)

    return "OK"

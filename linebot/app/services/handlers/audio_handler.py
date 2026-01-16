"""處理音訊訊息的模組"""

import aiofiles
import asyncio
from pathlib import Path
from linebot.v3.messaging import TextMessage
from app.services.handlers.common import (
    create_quick_reply,
    send_message,
    show_loading_animation,
)
from app.config.logger import get_logger
from app.config.line_config import messaging_api_blob
from app.api.audio import speech_to_text
from app.api.dify import inference

logger = get_logger(__name__)


def wait_for_audio_content(
    message_id: str, max_retries: int = 30, retry_delay: float = 0.5
):
    """等待音訊內容可用 (blocking，因為不使用要錢錢的 push API)"""
    for i in range(max_retries):
        try:
            message_content = messaging_api_blob.get_message_content(
                message_id, async_req=False
            )

            if message_content is not None and len(message_content) > 0:
                logger.info(
                    f"Got audio content after {i+1} retries, size: {len(message_content)} bytes"
                )
                return message_content
            else:
                logger.debug(f"Audio content not ready, retry {i+1}/{max_retries}")
                import time

                time.sleep(retry_delay)
                continue
        except Exception as e:
            logger.debug(
                f"Error getting audio content, retry {i+1}/{max_retries}: {str(e)}"
            )
            import time

            time.sleep(retry_delay)
            continue

    logger.error(f"Failed to get audio content after {max_retries} retries")
    return None


async def handle_audio_message(event):
    """處理音訊訊息"""
    user_id = event.source.user_id
    message_id = event.message.id
    audio_path = Path(f"audio_{user_id}_{message_id}.m4a")

    try:
        # 顯示載入動畫
        await show_loading_animation(user_id, 30)

        # 直接等待音訊內容可用
        message_content = wait_for_audio_content(message_id)

        if not message_content:
            logger.error(f"Failed to get message content for message_id: {message_id}")
            await send_message(
                event.reply_token,
                [
                    TextMessage(
                        text="無法取得音訊檔案，請稍後再試",
                        quick_reply=create_quick_reply(),
                    )
                ],
            )
            return

        logger.info(f"Got message content: {len(message_content)} bytes")

        # 寫入檔案
        async with aiofiles.open(audio_path, "wb") as f:
            await f.write(message_content)

        logger.info(f"Audio file saved: {audio_path}")

        # 轉錄音訊
        text = await speech_to_text(audio_path)

        if not text:
            await send_message(
                event.reply_token,
                [
                    TextMessage(
                        text="抱歉，無法辨識音訊", quick_reply=create_quick_reply()
                    )
                ],
            )
            return

        logger.info(f"Transcribed text: {text}")

        # 傳入 Dify API
        response_text = await inference(
            f"以下為語音轉文字內容，可能會有少量錯字：{text}", user_id
        )

        # 回覆轉錄結果
        await send_message(
            event.reply_token,
            [TextMessage(text=response_text, quick_reply=create_quick_reply())],
        )

    except Exception as e:
        logger.error(f"Failed to handle audio message: {str(e)}", exc_info=True)
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="處理音訊時發生錯誤，請稍後再試",
                    quick_reply=create_quick_reply(),
                )
            ],
        )
    finally:
        # 清理檔案
        if audio_path.exists():
            audio_path.unlink(missing_ok=True)
            logger.debug(f"Cleaned up audio file: {audio_path}")

from typing import Optional
from app.api.utils.providers import async_client
from app.config.logger import get_logger

logger = get_logger(__name__)


async def speech_to_text(
    audio_path: str, model: str = "gpt-4o-mini-transcribe", language: str = "zh"
) -> Optional[str]:
    """
    Convert speech to text using OpenAI API.

    Args:
        audio_path: Path to the audio file
        model: OpenAI model to use (default: gpt-4o-mini-transcribe)
        language: Language code (default: zh for Chinese)

    Returns:
        Transcribed text or None if conversion fails

    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If file is too large (>25MB)
    """
    try:
        # Validate file exists
        audio_data = open(audio_path, "rb")

        # Check file size (OpenAI limit is 25MB)
        if len(audio_data.read()) > 25 * 1024 * 1024:
            raise ValueError(
                f"Audio file too large: {len(audio_data) / (1024 * 1024):.1f}MB (max 25MB)"
            )

        logger.info(f"Converting audio to text: {audio_path}")

        converted_text = await async_client.audio.transcriptions.create(
            model=model,
            file=audio_data,
            language=language,
            response_format="text",
            prompt="輸入為台灣人的口音，內容多為洗腎、醫院相關，這個服務的名字叫「我在腎邊，你問我懂」",
        )

        logger.info(f"Successfully converted audio to text")
        return converted_text

    except FileNotFoundError as e:
        logger.error(f"Audio file not found: {audio_path}")
        return None
    except ValueError as e:
        logger.error(f"Invalid audio file: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Speech to text conversion failed: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    # 測試方法：到 linebot 目錄底下執行 uv run python -m app.api.audio
    import asyncio

    converted_text = asyncio.run(speech_to_text("test.mp3"))
    print(converted_text)

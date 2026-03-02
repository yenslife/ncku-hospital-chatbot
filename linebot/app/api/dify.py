"""Dify API client implementation for chat interactions."""

import logging
import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from functools import wraps
import time
import asyncio

import httpx
from dotenv import load_dotenv
from app.repositories.user_repository import UserRepository
from app.db.database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@dataclass
class DifyConfig:
    """Configuration for Dify API client."""

    api_key: str
    base_url: str = os.getenv("DIFY_BASE_URL", "")
    max_retries: int = 1
    retry_delay: float = 1.0


def retry_on_error(max_retries: int = 1, delay: float = 1.0):
    """Decorator for implementing retry logic."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPError, asyncio.TimeoutError) as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. Retrying..."
                    )
                    await asyncio.sleep(delay * (attempt + 1))
            return None

        return wrapper

    return decorator


class DifyClient:
    """Client for interacting with Dify API."""

    def __init__(self, config: DifyConfig, user_repository: UserRepository):
        self.config = config
        self.user_repository = user_repository
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the API configuration."""
        if not self.config.api_key:
            raise ValueError("DIFY_API_KEY is not set in environment variables")

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def _prepare_files(self, file_url: str) -> List[Dict[str, str]]:
        """Prepare files payload for API request."""
        return [{"type": "image", "transfer_method": "remote_url", "url": file_url}]

    @retry_on_error()
    async def inference(
        self, query: str, line_id: str = "abc-123", file_url: Optional[str] = None
    ) -> str:
        """
        Make an inference request to Dify API.

        Args:
            query: The user's query text
            line_id: The LINE user ID
            file_url: Optional URL to an image file

        Returns:
            str: The API response text

        Raises:
            httpx.HTTPError: If the API request fails
        """
        user = self.user_repository.get_user(line_id)

        payload = {
            "inputs": {},
            "query": "請分析這張圖片" if file_url else query,
            "response_mode": "streaming",  # 改用 streaming 模式避免連接超時
            "conversation_id": user.conversation_id or "",
            "user": line_id,
            "files": self._prepare_files(file_url) if file_url else None,
        }

        logger.info(f"Sending request to Dify API with payload: {payload}")

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.config.base_url}/chat-messages",
                    headers=self._prepare_headers(),
                    json=payload,
                ) as response:
                    logger.info(f"Received response with status code: {response.status_code}")
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Dify API error: {response.status_code} - {error_text.decode()}")
                        return f"Dify API 錯誤: {response.status_code}"
                    
                    # 收集 streaming 回應
                    full_response = ""
                    conversation_id = None
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])  # 移除 "data: " 前綴
                                
                                if data.get("event") == "message":
                                    full_response += data.get("answer", "")
                                elif data.get("event") == "message_end":
                                    conversation_id = data.get("conversation_id")
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    if conversation_id:
                        self.user_repository.update_conversation_id(line_id, conversation_id)
                        logger.info(f"Updated conversation ID: {conversation_id}")
                    
                    return full_response if full_response else "無法取得回應，請稍後再試"

        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            logger.error(f"API request error: {str(e)}")
            raise


# Create global config instance
config = DifyConfig(api_key=os.getenv("DIFY_API_KEY", ""))


# Provide async interface for Dify API inference
async def inference(
    query: str, line_id: str = "abc-123", files: Optional[str] = None
) -> str:
    """Async interface for Dify API inference."""
    db = SessionLocal()
    user_repository = UserRepository(db)
    try:
        dify_client = DifyClient(config, user_repository)
        return await dify_client.inference(query, line_id, files)
    except Exception as e:
        logger.error(f"Inference error: {str(e)}", exc_info=True)
        return "系統發生錯誤，請稍後再試"
    finally:
        db.close()


if __name__ == "__main__":
    pass

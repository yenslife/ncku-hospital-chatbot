from linebot.v3.messaging import (
    TextMessage,
    FlexMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
    FlexContainer,
)
from app.config.logger import get_logger
from app.config.line_config import line_bot_api
from app.services.utils import flex_message_convert_to_json
from app.repositories.user_repository import UserRepository
from app.services.handlers.common import (
    create_quick_reply,
    send_message,
    show_loading_animation,
)
from app.services.utils.flex_message import flex_message_convert_to_json

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

    # richmenu 的知識寶典
    if data == "postback_知識寶典":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        flex_message = FlexMessage(
            alt_text="知識寶典 flex",
            contents=FlexContainer.from_dict(
                flex_message_convert_to_json("flex_messages/知識寶典.json")
            ),
        )
        await send_message(
            event.reply_token,
            [flex_message],
        )
    elif data == "postback_常見問題":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        flex_message = FlexMessage(
            alt_text="常見問題 flex",
            contents=FlexContainer.from_dict(
                flex_message_convert_to_json("flex_messages/常見問題.json")
            ),
        )
        await send_message(
            event.reply_token,
            [flex_message],
        )
    elif data == "postback_洗腎原因":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="加護病房常見原因有：1酸血症：當血液中pH < 7.2或HCO3 < 15mmol/L；2電解質不平衡：特別是高血鉀(大於6mmol/L)、高血鈣(大於14mmol/L)；3中毒；4.身體水分過多：包含肺水腫；5尿毒症引發的相關症狀：常見情況包含尿毒症引起的腦病變、心包炎或出血等。"
                )
            ],
        )
    elif data == "postback_放置洗腎管路的風險":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="放置洗腎管路的主要風險包括感染（傷口紅腫熱痛、敗血症）、血管問題（血栓阻塞、狹窄、出血）、以及導管相關的併發症（滑脫、滲液、疼痛、活動受限）。不同管路（例如雙腔導管）風險與特性不同，但妥善的清潔、照護及定期追蹤是降低這些風險的關鍵。"
                )
            ],
        )
    elif data == "postback_洗腎費用":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="由全民健保給付費用，如果後須需要長期洗腎時，醫院會協助申請重大傷病卡，如果需要知道詳細的住院費用，可以在會客時間，詢問醫療團隊。"
                )
            ],
        )
    elif data == "postback_緊急洗腎風險":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="1. 心血管系統： 洗腎過程中脫水過多或透析液問題，可能導致血壓下降（低血壓）或上升（高血壓），造成心律不整、胸悶、心絞痛。\n\n2. 透析不平衡症候群： 剛開始洗腎者，血液中代謝廢物快速移除，可能引起頭痛、噁心、嘔吐、抽筋，甚至昏迷。\n\n3. 感染與出血： 緊急使用臨時導管（如雙腔靜脈導管）有增加感染和出血風險。"
                )
            ],
        )
    elif data == "postback_洗腎管路":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        flex_message = FlexMessage(
            alt_text="洗腎管路 flex message",
            contents=FlexContainer.from_dict(
                flex_message_convert_to_json("flex_messages/知識寶典_洗腎管路.json")
            ),
        )
        await send_message(
            event.reply_token,
            [flex_message],
        )
    elif data == "postback_雙腔導管":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="雙腔導管：常用於需要緊急洗腎的時候，但病人身上並沒有管路可以使用，管路常見於頸部或者鼠膝部兩處。不包含自體瘺管、人工動靜脈瘺管，因為在緊急洗腎的過程中，病人血流通常比較不穩定，如果使用瘺管風險較高。"
                )
            ],
        )
    elif data == "postback_永久性導管":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="永久性導管：病人原先就有放置永久性導管，常見於左、右鎖骨下方，遇到需要緊急洗腎時，就可以直接使用。"
                )
            ],
        )
    elif data == "postback_動靜脈瘻管":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        await send_message(
            event.reply_token,
            [
                TextMessage(
                    text="動靜脈瘻管：病人原先在手上就有放置，遇到緊急洗腎時，就可以直接使用。"
                )
            ],
        )
    elif data == "postback_洗腎迷思":
        logger.info(f"使用者 {user_display_name} {user_id} 點擊 {data} 按鈕")
        flex_message = FlexMessage(
            alt_text="洗腎迷思 flex message",
            contents=FlexContainer.from_dict(
                flex_message_convert_to_json("flex_messages/知識寶典_洗腎迷思.json")
            ),
        )
        await send_message(
            event.reply_token,
            [
                flex_message
            ],
        )

    # 未知的 postback
    else:
        logger.warning(
            f"未知的 postback data: {data} from {user_display_name} {user_id}"
        )
        await send_message(
            event.reply_token,
            [TextMessage(text=f"尚未實作此區域: {data}，請通知工程師")],
        )

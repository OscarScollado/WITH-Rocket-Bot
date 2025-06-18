from bernard.platforms.telegram.platform import Telegram, set_reply_markup
from aiohttp.web_request import Request
from bernard import layers as lyr
from bernard.layers import Stack
from bernard.platforms.telegram.layers import Update
from bernard.conf import settings


class TelegramMedia(Telegram):
    """
    BERNARD doesn't implement a way to send images via the Telegram API, so I did it myself.
    """

    def __init__(self):
        super().__init__()
        TelegramMedia.PATTERNS["media"] = "^Image (Update|Text InlineKeyboard?)?$"

        if settings.DEV:
            import logging

            logger = logging.getLogger("bernard.platform.telegram")
            logger.debug("Running in DEV mode")

    async def _send_media(self, request: Request, stack: Stack):
        """
        Base function for sending images.

        It supports adding a caption to the image and the Update layer.
        """

        # noinspection PyDeprecation,PyUnresolvedReferences
        chat_id = request.message.get_chat_id()
        lyr_image = stack.get_layer(lyr.Image)
        media = lyr_image.media

        msg = {
            "chat_id": chat_id
        }

        await set_reply_markup(msg, request, stack)

        if stack.has_layer(Update):
            update = stack.get_layer(Update)

            if update.inline_message_id:
                msg["inline_message_id"] = update.inline_message_id - 1
                del msg["chat_id"]
            else:
                msg["message_id"] = update.message_id - 1

            msg["media"] = {
                "type": "photo",
                "media": media
            }

            if hasattr(lyr_image, "caption"):
                msg["media"]["caption"] = lyr_image.caption

            await self.call(
                "editMessageMedia",
                {"Bad Request: image is not modified"},
                **msg
            )
        else:
            msg["photo"] = media

            if hasattr(lyr_image, "caption"):
                msg["caption"] = lyr_image.caption

            await self.call(
                "sendPhoto",
                **msg
            )


"""
My first attempt at this
(this code was written inside ".states/AskState")

if len(update) == 0:
    res = await self.responder.platform.call(
        "sendPhoto",
        photo="https://picsum.photos/1920/1080",
        chat_id=self.request.message.get_chat_id()
    )
else:
    import random
    param_num = random.randint(1, 100)
    res = await self.responder.platform.call(
        "editMessageMedia",
        media={
            "type": "photo",
            "media": f"https://picsum.photos/1920/1080?v={param_num}"
        },
        chat_id=self.request.message.get_chat_id(),
        message_id=context["message_id"]
    )

context["message_id"] = res["result"]["message_id"]
"""

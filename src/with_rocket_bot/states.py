from bernard import layers as lyr
from bernard.engine import BaseState
from bernard.i18n import translate as t
from bernard.platforms.telegram import layers as tgr
from .store import cs
from bernard.conf import settings

def get_frame_url(frame: int):
    """
    Gets the endpoint to request the frame.

    It depends on whether we are on DEV mode or not.
    :param frame: The position of the frame in the video
    """

    if settings.DEV:
        return f"{settings.TEST_API_URL}/frame/{frame}"
    else:
        from provider import video

        return video.get_frame_url(frame)

class WithRocketBotState(BaseState):
    """
    Root class for With Rocket Bot.

    Here you must implement "error" and "confused" to suit your needs. They
    are the default functions called when something goes wrong. The ERROR and
    CONFUSED texts are defined in `i18n/en/responses.csv`.
    """

    async def error(self) -> None:
        """
        This happens when something goes wrong (it's the equivalent of the
        HTTP error 500).
        """
        self.send(lyr.Text(t.ERROR))

    async def confused(self) -> None:
        """
        This is called when the user sends a message that triggers no
        transitions.
        """
        self.send(lyr.Text(t.CONFUSED))

    async def handle(self) -> None:
        raise NotImplementedError

class WelcomeState(WithRocketBotState):
    """
    This state just welcomes the user.
    """

    async def handle(self) -> None:
        self.send(lyr.Text("Welcome! Starting in a hot sec!"))

class AskState(WithRocketBotState):
    """
    The state that will be visited the most. The "main" state.

    It asks the user a binary question so the algorithm can continue running.
    """

    @cs.inject()
    async def handle(self, context) -> None:
        frame = context["frame"]
        if frame is None:
            raise ValueError("No frame to send!")

        lyr_image = lyr.Image(get_frame_url(context["frame"]))
        lyr_image.caption = f"Question number {context["count"]}"

        try:
            _ = self.request.get_layer(lyr.Postback).payload["action"]
        except (KeyError, ValueError):
            layers = [
                lyr_image,
                lyr.Text("Did the rocket launch yet?"),
                tgr.InlineKeyboard([[
                    tgr.InlineKeyboardCallbackButton(
                        text="Yes",
                        payload={"action": "yes"}
                    ),
                    tgr.InlineKeyboardCallbackButton(
                        text="No",
                        payload={"action": "no"}
                    )
                ]])
            ]
        else:
            layers = [
                lyr_image,
                tgr.Update()
            ]

        self.send(*layers)

class ByeState(WithRocketBotState):
    """
    This state reveals the frame found by the algorithm.
    """

    @cs.inject()
    async def handle(self, context) -> None:
        frame = context["frame"]
        if frame is None:
            raise ValueError("No frame to send!")

        self.send(lyr.Text("Getting the precise frame..."))
        self.send(lyr.Sleep(0.33))
        self.send(
            lyr.Image(get_frame_url(context["frame"])),
            lyr.Text(f"There you have it!")
        )

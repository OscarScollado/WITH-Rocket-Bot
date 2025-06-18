from dataclasses import dataclass
from typing import Literal
from aiohttp.web_request import Request
from bernard import layers as lyr
from bernard.engine.triggers import BaseTrigger
from .store import cs
from bernard.conf import settings

if settings.DEV:
    from dev_provider import video
else:
    from provider import video

@dataclass
class Bisection:
    """
    The algorithm that finds the frame.

    This is just a fancy word. The algorithm is the good old Binary Search.

    https://en.wikipedia.org/wiki/Binary_search
    """

    left: int
    right: int
    count: int
    frame: int

    @staticmethod
    def create(context=None):
        """
        Creates the bisection.
        :param context: An optional dictionary that populates the attrs.
        """

        if context is None:
            context = {}

        bisection = Bisection(
            left=context.get("left", video.info.first_frame),
            right=context.get("right", video.info.last_frame),
            count=context.get("count", 1),
            frame=0
        )
        bisection.frame = context.get("frame", bisection.half)
        return bisection

    @property
    def half(self) -> int:
        """
        Calculates the midpoint of the current state.
        """

        return (self.left + self.right) // 2

    @property
    def is_done(self) -> bool:
        """
        Tells whether the algorithm is done running.

        Since the algorithm always runs on the worst case, we can just
        compare the number of iterations against its time complexity
        in the worst case, which is "log n"

        "n" is the total number of frames.
        """

        return self.count > video.max_steps + 1

    def bisect(self, answer: Literal["yes", "no"]) -> None:
        """
        Performs the Binary Search algorithm.
        :param answer: This will tell whether we go towards the start or the end
        """

        if answer == "yes":
            self.right = self.frame
        elif answer == "no":
            self.left = self.frame
        else:
            raise ValueError(f"Invalid answer: {answer}")
        self.count += 1
        self.frame = self.half

class InitializationTrigger(BaseTrigger):
    """
    Setup trigger.

    It just initializes up a Bisection instance.
    """

    @cs.inject()
    async def rank(self, context) -> float:
        bisection = Bisection.create()
        context.update(bisection.__dict__)
        return 1.0

class BisectionTrigger(BaseTrigger):
    """
    The main flow of the FSM.

    Tells whether to go to the "finished" route or the "not finished" one.
    """

    def __init__(self, request: Request, finished: bool) -> None:
        super().__init__(request)
        self.finished = finished

    @cs.inject()
    async def rank(self, context) -> float:
        try:
            answer = self.request.get_layer(lyr.Postback).payload["action"]
        except (KeyError, ValueError, TypeError):
            return 0.0

        bisection = Bisection.create(context)
        bisection.bisect(answer)
        context.update(bisection.__dict__)
        return float(bisection.is_done == self.finished)

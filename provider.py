from functools import lru_cache
from math import floor, log2
from typing import NamedTuple
from urllib.parse import quote
from httpx import Client
import os


API_URL = os.getenv(
    "API_URL", "https://framex.with-madrid.dev/api/"
)
VIDEO_NAME = os.getenv(
    "VIDEO_NAME", "Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c"
)

class VideoInfo(NamedTuple):
    """
    Information from the video worked with
    """

    name: str
    width: int
    height: int
    frames: int
    frame_rate: int
    url: str
    first_frame: int
    last_frame: int

class Video:
    """
    Util function collection for video-related actions

    It uses the video from the FrameX API
    """

    def __init__(self):
        self.client = Client(timeout=30)

    @property
    @lru_cache
    def info(self) -> VideoInfo:
        """
        Fetches information about a video
        """

        response = self.client.get(f"{API_URL}video/{quote(VIDEO_NAME)}/")
        response.raise_for_status()
        data = response.json()
        data["first_frame"] = int(data["first_frame"].split("/")[-2])
        data["last_frame"] = int(data["last_frame"].split("/")[-2])
        return VideoInfo(**data)

    @property
    @lru_cache
    def max_steps(self) -> int:
        """
        Gets the steps required to find the frame
        """

        return floor(log2(self.info.frames))

    def get_frame_url(self, frame: int) -> str:
        """
        Gets the endpoint to request a frame
        :param frame: The position of the frame in the video
        """

        return f"{API_URL}video/{quote(VIDEO_NAME)}/frame/{quote(f"{frame}")}/"

    def setup_frame_endpoint(self):
        raise NotImplementedError("This is the production provider!")

video = Video()

from functools import lru_cache
from math import floor, log2
from typing import NamedTuple
import cv2
import os
from pathlib import Path
from sys import stderr
from aiohttp import web
from aiohttp.web_request import Request
from bernard.server.http import router


TEST_VIDEO_NAME = os.getenv(
    "TEST_VIDEO_NAME", "button.mp4"
)

def error(msg: str):
    """
    Convenience method for when an error occurs
    :param msg: The error message
    """

    print(msg, file=stderr)
    raise Exception(msg)

class VideoInfo(NamedTuple):
    """
    Information from the video worked with
    """

    name: str
    width: int
    height: int
    frames: int
    frame_rate: int
    uri: str
    first_frame: int
    last_frame: int

class Video:
    """
    Util function collection for video-related actions

    It uses a local video saved in the root directory
    """

    def __init__(self):
        self.video_path = str(Path(__file__).parent / TEST_VIDEO_NAME)
        self.video = cv2.VideoCapture(self.video_path)
        if not self.video.isOpened():
            error("Could not open video file")

    @property
    @lru_cache
    def info(self) -> VideoInfo:
        """
        Gets the video information
        """

        frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        return VideoInfo(
            name=TEST_VIDEO_NAME,
            width=int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            frames=frames,
            frame_rate=int(self.video.get(cv2.CAP_PROP_FPS)),
            uri="file://" + self.video_path,
            first_frame=0,
            last_frame=frames - 1,
        )

    @property
    @lru_cache
    def max_steps(self) -> int:
        """
        Gets the steps required to find the frame
        """

        return floor(log2(self.info.frames))

    def get_frame(self, frame: int) -> bytes:
        """
        Gets the requested frame
        :param frame: The position of the frame in the video
        """

        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame)

        ret, cv2_img = self.video.read()
        if not ret:
            error(f"Could not read frame {frame}")

        ret, buffer = cv2.imencode(".jpg", cv2_img)
        if not ret:
            error(f"Could not encode frame {frame}")

        return buffer.tobytes()

    def setup_frame_endpoint(self):
        """
        Mounts the endpoint used to request a frame

        For reference, the endpoint is: "/frame/{frame:int}"
        """

        async def serve_frame(request: Request):
            frame_number = int(request.match_info['frame'])
            try:
                data = self.get_frame(frame_number)
            except Exception as e:
                return web.Response(
                    status=404,
                    text=f"Frame not found: {e}"
                )
            else:
                return web.Response(
                    body=data,
                    content_type='image/jpeg',
                )
        router.add_get("/frame/{frame}", serve_frame)

    def __del__(self):
        self.video.release()

video = Video()

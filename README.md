# With Rocket Bot

Welcome to With Rocket Bot!

This is a project made by Óscar S. Collado with the [BERNARD framework](https://github.com/BernardFW/bernard).

You just need to type ``/start`` to start the bot in Telegram.


## Setup

In order to run the project, you just need to create a virtual env and then execute ``pip install -r requirements``.

Furthermore, a few env variables have been added on top of the ones that BERNARD has by default:

- ``API_URL``: the API URL, from where video data is fetched, goes apart from the ``BERNARD_BASE_URL``.
- ``TEST_API_URL``: API URL for testing purposes. Must be exposed to the Internet.
- ``DEV``: whether to work with the test video or the API video. ``DEBUG`` just controls the webserver's debug mode.
- ``TEST_VIDEO_NAME``: same as ``VIDEO_NAME``, but instead specifies the test video's name.


## What was made to make the code maintainable

The original structure of the BERNARD setup template was maintained.

On top of that, ``manage.py`` and ``settings.py`` have been extended to support a ``DEV``/testing mode.

Video-related utilities have been stored at root level, while the application-relevant
files have been put inside the ``src`` folder, just as the BERNARD framework recommends,
plus the ``TelegramMedia`` extension class.

The code follows a readable and concise pattern, making it easy to maintain along with
the stringdocs all over the application.

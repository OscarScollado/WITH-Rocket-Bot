from bernard.engine import Tr
from bernard.engine import triggers as trg
from bernard.i18n import intents as its
from bernard.platforms.telegram import layers as tgr
from .states import (
    WelcomeState,
    AskState,
    ByeState
)
from .triggers import (
    InitializationTrigger,
    BisectionTrigger
)

transitions = [
    Tr(
        dest=WelcomeState,
        factory=trg.Equal.builder(tgr.BotCommand("/start"))
    ),
    Tr(
        dest=AskState,
        origin=WelcomeState,
        factory=InitializationTrigger.builder(),
        internal=True
    ),
    Tr(
        dest=AskState,
        origin=AskState,
        factory=BisectionTrigger.builder(finished=False)
    ),
    Tr(
        dest=ByeState,
        origin=AskState,
        factory=BisectionTrigger.builder(finished=True)
    )
]

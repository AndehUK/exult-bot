from __future__ import annotations

import inspect
import platform
from enum import Enum
from types import TracebackType
from typing import (
    Any,
    Callable,
    List,
    NamedTuple,
    Optional,
    Self,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

from aiohttp import web

from helpers.logger import Logger

if TYPE_CHECKING:
    from bot import ExultBot


FuncT = TypeVar("FuncT", bound="Callable[..., Any]")


class Route(NamedTuple):
    name: str
    method: str
    func: Callable[..., Any]


class Methods(Enum):
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"


def route(name: str, *, method: Methods) -> Callable[[FuncT], FuncT]:
    def decorator(func: FuncT) -> FuncT:
        actual = func
        if isinstance(actual, staticmethod):
            actual = actual.__func__
        if not inspect.iscoroutinefunction(actual):
            raise TypeError("Route function must be a coroutine.")

        setattr(actual, "__ipc_route_name__", name)
        setattr(actual, "__ipc_method__", method.value)
        return func

    return decorator


class IPCBase:
    _runner: web.AppRunner
    _webserver: Optional[web.TCPSite]
    app: web.Application
    logger: Logger
    routes: List[Route]

    def __init__(self, bot: ExultBot) -> None:
        self.bot = bot
        self.logger = Logger("IPC")
        self.routes = []

        self.app = web.Application()
        self._runner = web.AppRunner(self.app)
        self._webserver = None

        for attr in map(lambda x: getattr(self, x, None), dir(self)):
            if attr is None:
                continue
            if (name := getattr(attr, "__ipc_route_name__", None)) is not None:
                route: str = attr.__ipc_method__
                self.routes.append(Route(func=attr, name=name, method=route))

        self.app.add_routes([web.route(x.method, x.name, x.func) for x in self.routes])

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def start(self, *, port: int = 3000) -> None:
        self.logger.debug("Starting IPC runner.")
        await self._runner.setup()
        self.logger.debug("Starting IPC webserver.")
        host = "localhost" if platform.system() == "Windows" else "0.0.0.0"
        self._webserver = web.TCPSite(self._runner, host, port=port)
        await self._webserver.start()

    async def close(self) -> None:
        self.logger.debug("Clearing up after IPCBase.")
        if self._webserver:
            try:
                await self._webserver.stop()
                self._webserver = None
            except RuntimeError as e:
                self.logger.error(f"Error stopping webserver: {e}")
        await self._runner.cleanup()

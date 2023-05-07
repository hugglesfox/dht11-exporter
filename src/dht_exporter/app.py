import contextlib

from . import settings
from .collectors import DhtCollector

from prometheus_client import make_asgi_app
from prometheus_client.core import REGISTRY

from starlette.applications import Starlette
from starlette.routing import Mount


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    with DhtCollector(settings.SYS_NAME) as collector:
        REGISTRY.register(collector)
        yield
        REGISTRY.unregister(collector)


app = Starlette(
    debug=settings.DEBUG or settings.LOG_LEVEL == "DEBUG",
    lifespan=lifespan,
    routes=[Mount("/metrics", make_asgi_app())],
)

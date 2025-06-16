import logging

import structlog
import orjson
from structlog import processors
from structlog.processors import JSONRenderer

from logs.config import Config, LogsRenderer

import datetime

import traceback


class AsyncBindableLogger(structlog.types.BindableLogger, structlog.stdlib.AsyncBoundLogger):  # type: ignore
    """Type fix for AsyncBoundLogger."""

#####
def exc_info_to_str(exc_info):
    if not exc_info:
        return None
    exc_type, exc_value, exc_tb = exc_info
    return ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

#####
def exc_info_to_str_processor(logger, method_name, event_dict):
    exc_info = event_dict.get("exc_info")
    if exc_info:
        event_dict["exc_info"] = exc_info_to_str(exc_info)
    return event_dict

##### solving problem with 'default' and not serializeable timedelta
def orjson_dumps(obj, *, default=None):
    def fallback(x):
        if isinstance(x, (datetime.datetime, datetime.date, datetime.timedelta)):
            return str(x)
        raise TypeError

    def fallback(x):
        if isinstance(x, (datetime.datetime, datetime.date, datetime.timedelta)):
            return str(x)
        # Try to convert SQLAlchemy model to dict if it has __dict__ or a custom method
        if hasattr(x, "__dict__"):
            # Or return a dict of relevant attributes
            return {k: v for k, v in vars(x).items() if not k.startswith('_')}
        # As last resort, convert unknown type to string
        return str(x)

    return orjson.dumps(obj, default=fallback).decode()

def startup(config: Config) -> None:
    # ... sets up structlog with AsyncBindableLogger
    pre_chain = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        #####
        exc_info_to_str_processor,
        structlog.processors.TimeStamper(fmt=config.time_format, utc=config.utc),
    ]

    handler = logging.StreamHandler()
    handler.set_name('default')
    handler.setLevel(config.level)

    if config.call_site:
        pre_chain.append(processors.CallsiteParameterAdder())

    if config.renderer == LogsRenderer.text:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    elif config.renderer == LogsRenderer.json:
        # renderer = JSONRenderer(
        #     serializer=lambda data: orjson.dumps(data).decode()
        #     # serializer=json.dumps
        #
        # )
        ##### solving problem with 'default' and not serializeable timedelta
        renderer = JSONRenderer(serializer=orjson_dumps)
    else:
        raise ValueError('Logging: Unknown renderer set')

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=pre_chain,  # type: ignore
    )
    handler.setFormatter(formatter)

    logging.basicConfig(handlers=(handler,), level=config.level)
    structlog.configure(
        processors=[
            *pre_chain,  # type: ignore
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=AsyncBindableLogger,
        cache_logger_on_first_use=True,
    )

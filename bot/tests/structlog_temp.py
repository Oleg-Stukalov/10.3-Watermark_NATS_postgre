import structlog
import inspect

logger = structlog.get_logger()

for method in ['debug', 'info', 'warning', 'error', 'critical', 'exception']:
    attr = getattr(logger, method, None)
    if attr is None:
        print(f"{method}: not found")
        continue

    if inspect.iscoroutinefunction(attr):
        print(f"{method}: ASYNC")
    else:
        print(f"{method}: SYNC")


# logger = structlog.get_logger()
# print(inspect.isawaitable(logger.info("test")))  # False for sync methods

### run in poetry from project ROOT: poetry run python bot/tests/structlog_temp.py
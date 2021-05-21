if "os" not in dir():
    import os
from loguru import logger

logger.add(os.getenv("PATH_LOG", "./log/local.log").replace('.log', '_{time:YYYY-MM-DD}.log'),
           format="{time:HH:mm:SSS} | {level}\t| {name}:{function}:{line} - {message}",
           rotation="10 MB",
           compression="zip")
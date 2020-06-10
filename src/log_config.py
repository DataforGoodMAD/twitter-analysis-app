import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
handler = logging.FileHandler("log")
handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
formatter = logging.Formatter(
    "%(asctime)s::%(levelname)s::%(lineno)d::%(filename)s::%(funcName)s::%(message)s"
)

handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(handler)

from starlette.config import Config

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
LOG_LEVEL = config("LOG_LEVEL", cast=str, default="INFO")
SYS_NAME = config("DHT_SYS_NAME", cast=str, default="iio:device0")

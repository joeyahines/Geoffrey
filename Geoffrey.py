""""
Geoffrey Minecraft Info Database

Created by: Joey Hines (ZeroHD)

"""
import logging
import logging.handlers as handlers
from bot import start_bot
from BotConfig import bot_config


def setup_logging():

    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.DEBUG)
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)

    handler = handlers.TimedRotatingFileHandler(filename='Geoffrey.log', when='D',
                                                interval=bot_config.rotation_duration, backupCount=bot_config.count,
                                                encoding='utf-8')

    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    discord_logger.addHandler(handler)
    sql_logger.addHandler(handler)


if __name__ == '__main__':
    setup_logging()
    start_bot()






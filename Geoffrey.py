""""
Geoffrey Minecraft Info Database

Created by: Joey Hines (ZeroHD)

"""
import logging
import logging.handlers as handlers
import bot
from BotConfig import bot_config
from sys import stdout


def setup_logging():

    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)
    bot_info_logger = logging.getLogger('bot')
    bot_info_logger.setLevel(logging.INFO)

    handler = handlers.TimedRotatingFileHandler(filename='Geoffrey.log', when='D',
                                                interval=bot_config.rotation_duration, backupCount=bot_config.count,
                                                encoding='utf-8')

    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    console = logging.StreamHandler(stdout)

    console.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    discord_logger.addHandler(handler)
    sql_logger.addHandler(handler)
    bot_info_logger.addHandler(handler)
    bot_info_logger.addHandler(console)


if __name__ == '__main__':
    print("Starting logging...")
    setup_logging()
    print("Starting bot...")
    bot.start_bot()

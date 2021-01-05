#!/usr/bin/python3

# foxhunt72
# telegram bot

from telegram.ext import Updater
import logging
from pprint import pprint
import os
import sys

# init logger
logger = logging.getLogger('buttler_bot')
hdlr = logging.FileHandler(os.path.expanduser('~/buttler_bot.log'))
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
hdout=logging.StreamHandler(sys.stdout)
hdout.setFormatter(formatter)
logger.addHandler(hdout)
logger.setLevel(logging.INFO)

config_file="~/.config/buttler_bot/config.yml"
config_expand=os.path.expanduser(config_file)

try:
  from yaml import safe_load as yaml_load
except:
  from yaml import load as yaml_load

try:
  with open(config_expand,'r') as file:
    config=yaml_load(file)
except:
  print("""
    Needs a config file: %s
    with minimal:
 
    ---
    telegram_bot_token: <your telegram bot token>
    my_user_id: <your used id>
    commands:
      - text: <text to response to>
        command: <command to run>
        help: <help message>

    """ % config_expand)
  exit(1)

for i in ['telegram_bot_token','my_user_id', 'commands']:
  if not i in config:
    logger.error('missing value in <%> config file' % i)
    exit(1)

try:
  if len(config['commands']) == 0:
    logger.error('missing commands in config file')
    exit(2)
except:
  logger.error('issue reading config <commands> section.')
  exit(3)

updater = Updater(token=config['telegram_bot_token'], use_context=True)
import subprocess
version = '0.2'


my_user_id=config['my_user_id']

dispatcher = updater.dispatcher


def start(update, context):
    if update.effective_chat.id == my_user_id:
      context.bot.send_message(chat_id=update.effective_chat.id, text="I am here, what can i do for you.")

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def run_command(command_str):
    logger.info('run_command: %s' % command_str)
    output = subprocess.getoutput(command_str)
    if output == "":
      output = "return ok"
    return(output)

def echo(update, context):
    logger.debug(update.effective_chat.id)
    #import pdb; pdb.set_trace()

    if update.effective_chat.id == my_user_id:
      my_text=update.message.text.lower()
      return_text=update.message.text
      if my_text == 'ping':
        logger.info('ping/pong')
        return_text = 'pong '+version
      for i in config['commands']:
        if my_text == i['text']:
          logger.info('found text: %s' % i['text'])
          if 'command' in i:
            return_text=run_command(i['command'])
          else:
            return_text='no command for <%s>' % i['text']
          continue
      if my_text == 'help':
        return_text = """
          Dit is de help text
        """
        for i in config['commands']:
          help_str = i['help'] if 'help' in i else ''
          return_text += "\n"+"  %s: %s" % (i['text'],help_str)
      context.bot.send_message(chat_id=update.effective_chat.id, text=return_text)

from telegram.ext import MessageHandler, Filters
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

logger.info('starting buttler_bot')
updater.start_polling()

#!/usr/bin/python

# foxhunt72
# testing telegram bot

from telegram.ext import Updater
from pprint import pprint
import os

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
    print('missing value in <%> config file' % i)
    exit(1)

try:
  if len(config['commands']) == 0:
    print('missing commands in config file')
    exit(2)
except:
  print('issue reading config <commands> section.')
  exit(3)

updater = Updater(token=config['telegram_bot_token'], use_context=True)
import subprocess
version = '0.1'


my_user_id=config['my_user_id']

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(update, context):
    if update.effective_chat.id == my_user_id:
      context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def run_command(command_str):
    output = subprocess.getoutput(command_str)
    if output == "":
      output = "return ok"
    return(output)

def echo(update, context):
    print(update.effective_chat.id)
    if update.effective_chat.id == my_user_id:
      my_text=update.message.text.lower()
      return_text=update.message.text
      if my_text == 'ping':
        return_text = 'pong '+version
      for i in config['commands']:
        print('check: <%s> <%s>' % (my_text,i['text']))
        if my_text == i['text']:
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

updater.start_polling()

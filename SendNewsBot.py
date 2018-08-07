# ==========================
#  general python modules
# ==========================
import feedparser
import os
import numpy as np
from functools import wraps
import sys
from threading import Thread
import datetime

# ===========================
# python-telegram-bot modules
# ===========================
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram as telegram

# ===================================
# create folder for database of users
# ===================================
if not os.path.exists('users'):
    os.makedirs('users')

# ===============================
# load admin list
# ===============================
fid = open('./admin_only/admin_list.txt', 'r')
LIST_OF_ADMINS = [int(adm) for adm in fid.readline().split()]
fid.close()


# ===============================================================
# The following function reads the TOKEN from a file.
# This file is not incuded in the github-repo for obvious reasons
# ===============================================================
def read_token(filename):
    with open(filename) as f:
        token = f.readline().replace('\n', '')
    return token


# ==========================
# restriction decorator
# ==========================
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            bot.send_message(chat_id=update.message.chat_id, text="You are not authorized to run this command")
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


# ==========================
# start - welcome message
# ==========================
def start(bot, update):

    msg = "This bot send news about a selected topic.\n"
    msg += "In this group the topic is: <strong>Google/Android</strong> \n\n"

    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

    # add user to database for future communications
    current_users = str(update.message.chat_id)

    # merge it to the existing database and filter duplicates
    if os.path.exists('./users/users_database.db'):
        user_db = []
        with open('./users/users_database.db', 'r') as fid:
            for line in fid:
                user_db.append(int(line))
        user_db.append(int(current_users))
        user_db = np.unique(user_db)
        np.savetxt('./users/users_database.db', user_db, fmt="%s")
    else:
        np.savetxt('./users/users_database.db', [int(current_users)], fmt="%s")


# ==========================
# help - short guide
# ==========================
def help(bot, update):
    msg = "The *SendNewsBot* is really simple to be used.\n\n"
    msg += "You just need to activate it.\n\n"
    msg += "The bot will send you information on a daily basis."

    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)


# =====================================================
# daily_report report to all users
# =====================================================
def daily_report(bot, update):
    feed = list()
    # android
    feed.append(feedparser.parse('https://www.google.com/alerts/feeds/03166883211171261052/1353638956941984046'))
    # google pixel
    feed.append(feedparser.parse('https://www.google.com/alerts/feeds/03166883211171261052/17750017897550226590'))
    # WARNING: the two links above should be updated by the one who administrates the bot

    # create message
    msg = ''
    for rss_feed in feed:
        for n, entry in enumerate(rss_feed['entries']):
            msg += str(n + 1) + ') <b>' + entry['title'].replace('<b>','').replace('</b>','') + '</b>\n'
            msg += '<a href="'
            msg += entry['link'] + '">link</a>\n\n'

    # send message to all users (keeping track of the incative ones)
    users = np.loadtxt('./users/users_database.db').reshape(-1,)
    inactive_users = []
    for index, single_user in enumerate(users):
        chat_id = int(single_user)
        # try to send the message
        try:
            bot.send_message(chat_id=chat_id,
                             text=msg,
                             parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

        # if the user closed the bot, cacth exception and update inactive_users
        except telegram.error.TelegramError:
            inactive_users.append(index)

    # ==================================================================================================
    # uncomment next block if you want to:
    #     * remove inactive users from database
    #     * send report to all ADMINS about active and inactive users

    # # summary
    # N_active = users.size - len(inactive_users)
    # N_inactive = len(inactive_users)
    #
    # # send summary to admins
    # msg = '*Summary*:\n'
    # msg += '  \* active users notified: {:d}\n'.format(N_active)
    # msg += '  \* inactive users (removed): {:d}'.format(N_inactive)
    # for single_user in LIST_OF_ADMINS:
    #     chat_id = int(single_user)
    #     # try to send the message
    #     try:
    #         bot.send_message(chat_id=chat_id,
    #                          text=msg,
    #                          parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
    #
    #     # if the admin closed the bot, cacth exception and do nothing
    #     except telegram.error.TelegramError:
    #         pass
    #
    # # remove inactive_users and update database
    # users = np.delete(users, inactive_users)
    # np.savetxt('./users/users_database.db', users.astype(int), fmt="%s")
    # ==================================================================================================


# =====================================================
# send_report report to a single users
# =====================================================
def send_report(bot, update):
    feed = list()
    # android
    feed.append(feedparser.parse('https://www.google.com/alerts/feeds/03166883211171261052/1353638956941984046'))
    # google pixel
    feed.append(feedparser.parse('https://www.google.com/alerts/feeds/03166883211171261052/17750017897550226590'))
    # WARNING: the two links above should be updated by the one who administrates the bot

    # create message
    msg = ''
    for rss_feed in feed:
        for n, entry in enumerate(rss_feed['entries']):
            msg += str(n + 1) + ') <b>' + entry['title'].replace('<b>','').replace('</b>','') + '</b>\n'
            msg += '<a href="'
            msg += entry['link'] + '">link</a>\n\n'

    try:
        bot.send_message(chat_id=update.message.chat_id,
                         text=msg,
                         parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
    except telegram.error.TelegramError:
        pass


# =========================================
# unknown - catch any wrong command
# =========================================
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


# =========================================
# building the bot behaviour
# =========================================
def main():
    # set TOKEN and initialization
    # (the file including the TOKEN is not incuded in the github-repo for obvious reasons)
    fname = './admin_only/SendNewsBot_token.txt'
    updater = Updater(token=read_token(fname))
    dispatcher = updater.dispatcher

    # define a job
    job_queue = updater.job_queue
    # define the time to send the report every day
    hour = 19
    minute = 0
    second = 0
    job_daily = job_queue.run_daily(daily_report, datetime.time(hour, minute, second))

    # code to restart the bot
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @restricted
    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    # /r - restart the bot (handler)
    dispatcher.add_handler(CommandHandler('r', restart))

    # /start handler
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # /help handler
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    # /send_report - send message to all users
    send_report_handler = CommandHandler('send_report', send_report)
    dispatcher.add_handler(send_report_handler)

    # reply to unknown commands
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # start the BOT
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


# ===========
# run the bot
# ===========
if __name__ == '__main__':
    main()
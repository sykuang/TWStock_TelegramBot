# -*- coding: UTF-8 -*-
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from DataProvider import fugle, yahoo
import datetime
import os
TOKEN_TG = os.getenv("TOKEN_TG")
TOKEN_FUGLE = os.getenv("TOKEN_FUGLE")
updater = Updater(token=TOKEN_TG, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


rtProvider = fugle.fugle(TOKEN_FUGLE)
htProvider = yahoo.yahoo()


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def echo(update, context):
    query = update.message.text
    ret = rtProvider.getStockInfo(query)
    result_str = ret['ID']+" "+ret['Name']+"的即時股價: "+str(ret['RealPrice'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=result_str)
    ret['photo'].seek(0)
    context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=ret['photo'])
    tendayMA_str = ("5日線:%.2f" % htProvider.getMA(query, "5d"))
    moMA_str = ("月線:%.2f" % htProvider.getMA(query, "1mo"))
    context.bot.send_message(chat_id=update.effective_chat.id, text=tendayMA_str+"\n"+moMA_str)

def inline_caps(update, context):
    query = update.inline_query.query
    if not query or len(query) < 4:
        return
    try:
        results = list()
        ret = rtProvider.getStockInfo(query)
        result_str = ret['ID']+" "+ret['Name']+"的即時股價: "+str(ret['RealPrice'])
        results.append(
            InlineQueryResultArticle(
                id=query.upper(),
                title=ret['ID']+" "+ret['Name']+"的即時股價",
                input_message_content=InputTextMessageContent(result_str),
            )
        )
        context.bot.answer_inline_query(update.inline_query.id, results)
    except:
        return


def notify(context):
    symbolId = context.job.context[1]
    price = context.job.context[2]
    chat_id = context.job.context[0]
    stockInfo = rtProvider.getStockInfo(symbolId)
    if stockInfo['RealPrice'] <= price:
        context.bot.send_message(
            chat_id, text=stockInfo['ID']+" "+stockInfo['Name']+"目前的價格:"+str(stockInfo['RealPrice']))
        context.job.schedule_removal()


def removeNotify(context):
    job = context.job.context[1]
    job.schedule_removal()


def maPriceChecker(context):
    symbolId = context.job.context[1]
    price = context.job.context[2]
    chat_id = context.job.context[0]
    ma = htProvider.getMA(symbolId)
    notify_price = (1.0+(price/100))*ma
    context.bot.send_message(chat_id, text="設定到價 %s 月線：%.2f 的 %d %%(%f)" % (
        symbolId, ma, price, notify_price))
    new_job = context.job_queue.run_repeating(
        notify, 30, context=[chat_id, symbolId, notify_price])
    dt = datetime.time(
        13, 20, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
    context.job_queue.run_once(removeNotify, dt, context=[symbolId, new_job])


def set_Notify(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        symbolId = context.args[0]
        price = int(context.args[1])
        if price < 0 or price > 100:
            update.message.reply_text("請設定%數(0-100))")
            return
        jobId = symbolId+"_start"
        # Add job to queue and stop current one if there is a timer already
        if jobId in context.chat_data:
            context.chat_data[jobId].schedule_removal()
        dt = datetime.time(8, 55, 0, tzinfo=datetime.timezone(
            datetime.timedelta(hours=8)))
        new_job = context.job_queue.run_daily(maPriceChecker, dt, days=(
            1, 2, 3, 4, 5), context=[chat_id, symbolId, price])
        context.chat_data[jobId] = new_job

        update.message.reply_text('到價通知設定完成')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set 代號 %數')


def unset_Notify(update, context):
    chat_id = update.message.chat_id
    try:
        symbolId = context.args[0]
        jobId = symbolId+"_start"
        if jobId in context.chat_data:
            update.message.reply_text("移除 %s 到價通知" % symbolId)
            context.chat_data[jobId].schedule_removal()
            del context.chat_data[jobId]
    except:
        update.message.reply_text('Usage: /unset 代號')


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def main():
    #Add start handler
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    #Add echo handler
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    #Add unknow cmd handler

    #Add inline handler
    inline_caps_handler = InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)
    dispatcher.add_handler(CommandHandler("set", set_Notify,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("unset", unset_Notify,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    # start robot
    updater.start_polling()


if __name__ == '__main__':
    main()

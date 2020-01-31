# -*- coding: UTF-8 -*-
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from fugle_realtime import intraday
import os
TOKEN_TG = os.getenv("TOKEN_TG")
TOKEN_FUGLE = os.getenv("TOKEN_FUGLE")
updater = Updater(token=TOKEN_TG, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def getStockInfo(id):
    ret = dict()
    output = intraday.trades(apiToken=TOKEN_FUGLE,
                             output="dataframe", symbolId=id)
    output_meta = intraday.meta(
        apiToken=TOKEN_FUGLE, output="dataframe", symbolId=id)
    # except:
    # print("Get Data Error")
    # raise Exception("Get Data Error")
    ret['Name'] = output_meta.iloc[0, output_meta.columns.get_loc("nameZhTw")]
    ret['RealPrice'] = str(output.iloc[-1, output.columns.get_loc("price")])
    ret['ID'] = id
    return ret


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=getStockInfo(
        update.message.text)['RealPrice'])


def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    ret = getStockInfo(query)
    result_str = ret['ID']+" "+ret['Name']+"的即時股價: "+ret['RealPrice']
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title=query,
            input_message_content=InputTextMessageContent(result_str),
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


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
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    #Add inline handler
    inline_caps_handler = InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)
    # start robot
    updater.start_polling()


if __name__ == '__main__':
    main()

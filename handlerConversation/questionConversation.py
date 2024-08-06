from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler

from bot.handlers.basic_commands import cancel
from bot.handlers.question_handler import question_command, answers_response, difficulty_response, user_answer_response, \
    topic_response

DIFFICULTY, ANSWERS, TOPIC, USER_ANSWER = range(4)


def question_conversation():
    question_conv = ConversationHandler(
        entry_points=[CommandHandler('question', question_command)],
        states={
            DIFFICULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, difficulty_response)],
            ANSWERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, answers_response)],
            TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, topic_response)],
            USER_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_answer_response)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    return question_conv

import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.setting.config import config

def get_difficulty_keyboard():
    difficulty_button1 = KeyboardButton("easy")
    difficulty_button2 = KeyboardButton("medium")
    difficulty_button3 = KeyboardButton("hard")
    difficulty_button4 = KeyboardButton("none")
    return ReplyKeyboardMarkup(
        [[difficulty_button1, difficulty_button2], [difficulty_button3, difficulty_button4]], 
        resize_keyboard=True, one_time_keyboard=True
    )

def get_answers_keyboard():
    answers_button1 = KeyboardButton("1")
    answers_button2 = KeyboardButton("2")
    answers_button3 = KeyboardButton("3")
    answers_button4 = KeyboardButton("4")
    return ReplyKeyboardMarkup(
        [[answers_button1, answers_button2], [answers_button3, answers_button4]], 
        resize_keyboard=True, one_time_keyboard=True
    )

DIFFICULTY, ANSWERS, TOPIC, USER_ANSWER = range(4)

async def question_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Choose difficulty level:", reply_markup=get_difficulty_keyboard())
    return DIFFICULTY

async def difficulty_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    difficulty = update.message.text
    if difficulty not in ["easy", "medium", "hard", "none"]:
        await update.message.reply_text("Invalid difficulty. Please choose from the keyboard options.")
        return DIFFICULTY

    context.user_data['difficulty'] = difficulty
    await update.message.reply_text("Enter number of answers:", reply_markup=get_answers_keyboard())
    return ANSWERS

async def answers_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    num_of_answers = update.message.text

    if num_of_answers not in ["1", "2", "3", "4"]:
        await update.message.reply_text("Invalid number of answers. Please choose from the keyboard options.")
        return ANSWERS

    context.user_data['num_of_answers'] = num_of_answers
    await update.message.reply_text("Enter a topic:")
    return TOPIC

async def handle_open_question_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    difficulty = context.user_data['difficulty']

    response = requests.post(
        f"{config.SERVER_URL}/questions/", 
        json={"difficulty": difficulty, "subject": topic}
    ).json()

    context.user_data['question_text'] = response["question_text"]
    context.user_data['options'] = response["options"]
    context.user_data['correct_answer'] = response["correct_answer"]
    context.user_data['options'] = [response["options"]]

    reply = f"Question: {response['question']}\n"
    await update.message.reply_text(reply)
    
    return USER_ANSWER

async def handle_closed_question_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    difficulty = context.user_data['difficulty']
    num_of_answers = context.user_data['num_of_answers']

    response = requests.post(
        f"{config.SERVER_URL}/questions/", 
        json={"difficulty": difficulty, "subject": topic, "answers_count": num_of_answers}
    ).json()

    context.user_data['question_text'] = response["question_text"]
    context.user_data['options'] = response["options"]
    context.user_data['correct_answer'] = response["correct_answer"]
    context.user_data['details'] = response["details"]

    reply = f"Question: {response['question_text']}\n"
    for i, answer in enumerate(response["options"]):
        reply += f"({i+1}) {answer}.\n"
    
    await update.message.reply_text(reply)
    
    return USER_ANSWER

async def topic_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    context.user_data['topic'] = topic

    if context.user_data['num_of_answers'] == "1":
        return await handle_open_question_topic(update, context)
    else:
        return await handle_closed_question_topic(update, context)

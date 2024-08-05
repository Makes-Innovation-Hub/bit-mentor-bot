import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.setting.config import config

difficulty_button1 = KeyboardButton("easy")
difficulty_button2 = KeyboardButton("medium")
difficulty_button3 = KeyboardButton("hard")
difficulty_button4 = KeyboardButton("none")
difficulty_keyboard = ReplyKeyboardMarkup(
    [[difficulty_button1, difficulty_button2, difficulty_button3, difficulty_button4]],
    resize_keyboard=True, one_time_keyboard=True)

answers_button1 = KeyboardButton("1")
answers_button2 = KeyboardButton("2")
answers_button3 = KeyboardButton("3")
answers_button4 = KeyboardButton("4")
answers_keyboard = ReplyKeyboardMarkup([[answers_button1, answers_button2], [answers_button3, answers_button4]],
                                       resize_keyboard=True, one_time_keyboard=True)

DIFFICULTY, ANSWERS, TOPIC, USER_ANSWER = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, public_ip: str) -> None:
    message = f"Hello! This is your bot.\nPublic IP: {public_ip}"
    await update.message.reply_text(message)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "To get a question you need to use /question\nYou will be asked to enter the required information\nFirst you "
        "need to enter a diffic ulty\nThen enter the number of answers\nThen enter the topic")


async def question_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Choose difficulty level:", reply_markup=difficulty_keyboard)
    return DIFFICULTY


async def difficulty_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    difficulty = update.message.text
    if difficulty and difficulty.lower() not in ["easy", "medium", "hard", "none"]:
        await update.message.reply_text("Invalid difficulty. Please choose from the keyboard options.")
        return DIFFICULTY

    context.user_data['difficulty'] = difficulty
    await update.message.reply_text("Enter number of answers:", reply_markup=answers_keyboard)
    return ANSWERS


async def answers_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    num_of_answers = update.message.text
    if num_of_answers not in ["1", "2", "3", "4"]:
        await update.message.reply_text("Invalid number of answers. Please choose from the keyboard options.")
        return ANSWERS

    context.user_data['num_of_answers'] = num_of_answers
    await update.message.reply_text("Enter a topic:")
    return TOPIC


async def topic_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    context.user_data['topic'] = topic
    difficulty = context.user_data['difficulty']
    num_of_answers = context.user_data['num_of_answers']
    gen_question_req_body = {"difficulty": difficulty, "topic": topic}
    if int(num_of_answers) > 1:
        gen_question_req_body["answers_count"] = num_of_answers
        try:
            response = requests.post(f"{config.SERVER_URL}/generate-question", json=gen_question_req_body).json()
            question = response["question"]
            answers = response["optional_answers"]
            context.user_data['question'] = question
            context.user_data['answers'] = answers
            context.user_data["correct_answer"] = response["correct_answer"] if "correct_answer" in response else 0
            reply = f"Question: {question[0]}\n"
            if int(num_of_answers) > 1:
                for i, answer in enumerate(answers):
                    reply += f"({i + 1}) {answer[0]}.\n"
            await update.message.reply_text(reply)
            return USER_ANSWER
        except Exception as e:
            print("error in gen question: ", e)
            return -1


async def user_answer_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_answer = update.message.text
    correct_answer = context.user_data['corect_answer'] + 1

    if int(user_answer) == correct_answer:
        await update.message.reply_text("Correct!")
    else:
        await update.message.reply_text(f"Wrong! The correct answer is {correct_answer}.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(f"{config.SERVER_URL}/")
        response.raise_for_status()
        data = response.json()
        await update.message.reply_text(data["message"])
    except requests.RequestException as e:
        await update.message.reply_text(f"Error fetching data: {e}")

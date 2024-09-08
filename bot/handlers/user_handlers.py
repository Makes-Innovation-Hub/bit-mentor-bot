import requests
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config.logging_config import app_logger
from bot.setting.config import config
from bot.utils.jwt_utils import create_jwt

def check_answer_with_openai(question, user_answer, user_id):
    """
    Checks if a user's answer is correct by sending a request to OpenAI.

    Args:
        question (str): The question being asked.
        user_answer (str): The user's answer to the question.

    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    try:
        data = {
            "question": question,
            "user_answer": user_answer
        }
        token = create_jwt(user_id)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        app_logger.info(f"Sending answer check to OpenAI for question: {question}")
        response = requests.post(f"{config.SERVER_URL}/check_answer", json=data, headers=headers)
        result = response.json()
        app_logger.info(f"Received answer check result: {result}")
        return result["score"]
    except requests.RequestException as e:
        app_logger.error(f"Request error during answer check: {e}")
        return False
    except Exception as e:
        app_logger.error(f"Unexpected error during answer check: {e}")
        return False


async def handle_open_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handles an open question by checking the user's answer against the correct answer using OpenAI.

    Returns:
        bool: True if the user's answer is correct, False otherwise.
    """
    try:
        user_answer = update.message.text
        question_text = context.user_data['question_text']
        score = check_answer_with_openai(question_text, user_answer, update.effective_user.id)
        correct_answer = context.user_data['correct_answer']
        app_logger.info(
                f"User {update.effective_user.username} ({update.effective_user.id}) provided answer: {user_answer} for open question: {question_text}")

        if score > 0:
            await update.message.reply_text(f"Correct! your score is {score}. \n")
            app_logger.info("User provided the correct answer.")
        else:
            await update.message.reply_text(f"Wrong! The correct answer is {correct_answer}.\n")
            app_logger.info("User provided an incorrect answer.")
        explanation = f"Explanation:\n{context.user_data['details'][0]}"
        
        await update.message.reply_text(explanation)
        app_logger.info("Sent explanation to user.")
        return score
    except Exception as e:
        app_logger.error(
            f"Error handling open question for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error processing your answer. Please try again later.")
        return False
    


async def handle_closed_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handles a closed question by checking the user's answer against the correct answer.

    Returns:
        bool: True if the user's answer is correct, False otherwise.
    """
    try:
        user_answer = update.message.text
        correct_answer = context.user_data['correct_answer'] + 1
        app_logger.info(
                f"User {update.effective_user.username} ({update.effective_user.id}) provided answer: {user_answer} for closed question with correct answer: {correct_answer}")

        is_correct = int(user_answer) == correct_answer
        score = 0
        if is_correct:
            await update.message.reply_text("Correct!\n")
            score=10
            app_logger.info("User provided the correct answer.")
        else:
            await update.message.reply_text(f"Wrong! The correct answer is {correct_answer}.\n")
            app_logger.info("User provided an incorrect answer.")
        explanation = "Explanation:\n"
        explanation += f"({correct_answer}) {context.user_data['details'][correct_answer-1]}.\n"
        await update.message.reply_text(explanation)
        app_logger.info("Sent explanation to user.")
        return score
    except Exception as e:
        app_logger.error(
            f"Error handling closed question for user {update.effective_user.username} ({update.effective_user.id}): {e}")
        await update.message.reply_text("There was an error processing your answer. Please try again later.")
        return False


async def user_answer_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handles the user's answer response by storing the user's answer, 
        determining whether the answer is correct, and updating the user's stats.

        Args:
            update (Update): The update object containing the user's message.
            context (ContextTypes.DEFAULT_TYPE): The context object containing the conversation state.

        Returns:
            int: The next state in the conversation flow.
        """
        context.user_data['users'] = []
        user_answer = update.message.text
        user_id = update.message.from_user.id
        user_entry = {'user_id': user_id, 'answer': user_answer}
        context.user_data['users'].append(user_entry)
        if context.user_data['num_of_answers'] == "1":
            score = await handle_open_question(update, context)
        else:
            score = await handle_closed_question(update, context)
        answer_data = {
            'user_id': user_id,
            'subject': context.user_data['topic'],
            'difficulty': context.user_data['difficulty'],
            'score': score
        }
        try:
            token = create_jwt(user_id)
            headers = {
            'Authorization': f'Bearer {token}'
            }
            save_response = requests.post(f"{config.SERVER_URL}/update-user-stat", json=answer_data, headers=headers).json()
            app_logger.info(f"User stats updated successfully for user {user_id}.")
        except requests.RequestException as e:
            app_logger.error(f"Request error when updating user stats for user {user_id}: {e}")
        try:
            token = create_jwt(user_id)
            headers = {
            'Authorization': f'Bearer {token}'
            }
            response = requests.post(f"{config.SERVER_URL}/insert-question", json=context.user_data, headers=headers)
            app_logger.info(f"Question data inserted successfully for user {user_id}.")
        except requests.RequestException as e:
            app_logger.error(f"Request error when inserting question data for user {user_id}: {e}")
        return ConversationHandler.END
  

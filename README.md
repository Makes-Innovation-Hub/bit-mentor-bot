# Bit Mentor Bot

## Table of Contents
- [Team Members](#team-members)
- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Workflow](#workflow)

## Team Members
- **Muhammad Sarahni**
- **Adam Kaabiya**
- **Najeeb Ibrahim**
- **Maysa Zbidat**
- **Aseel Khamis**

## Overview
The Bit Mentor Bot is a Telegram bot designed to interact with users by asking questions and providing answers in a multiple-choice question (MCQ) format. It communicates with a backend server to fetch questions and submit answers.

## Architecture

### Components
1. **python-telegram-bot**:
    - A Python library that allows the bot to interact with Telegram users, handling messaging and commands.
2. **FastAPI Server**:
    - The backend server that the bot communicates with to fetch and submit questions and answers. (Hosted in a separate repository)

### Diagram
The bot part this reposotory, but the diagram entails the entire project
![bot](https://github.com/user-attachments/assets/8f0ff1d0-58c1-48ef-a2dc-343d8de97c26)

**add picture/diagram workflow

### General Architecture
- **Telegram Bot**: Interacts with users, sending and receiving messages through the `python-telegram-bot` library.
- **FastAPI Server**: Handles requests from the Telegram bot, processes them, and returns appropriate responses (detailed in the separate server repository).

## Workflow

1. **User Interaction**:
    - Users interact with the Telegram bot by sending messages and commands.
2. **API Requests**:
    - The Telegram bot sends API requests to the FastAPI server to fetch questions and submit answers.(including the correct/wrong answer but hidden)
3. **Response**:
    - The FastAPI server processes these requests and sends appropriate responses back to the Telegram bot, which then communicates these responses to the user.

## Technologies

- **Bot Framework**: [python-telegram-bot](https://python-telegram-bot.org/)
- **Backend Server**: [FastAPI](https://fastapi.tiangolo.com/) (details in separate repository)
- **Hosting**: [AWS](https://aws.amazon.com/)


## Enviroment variables  
* For Dev

- `SERVER_URL_DEV`: Url of server. (from .env_dev)
- `BOT_TOKEN_DEV`: token of bot. (from .env_dev)

* For Prod

- `SERVER_URL_PROD`: Url of server. (from .env_prod)
- `BOT_TOKEN_PROD`: token of bot. (from .env_prod)

## How to run
 
 In the root directory, open terminal and run these commands:        
1.Install the required packages:    

``` pip install -r requirements.txt ```

 2.Run the Bot    
* for Development    
``` 
python -m bot.main --env dev 
 ``` 
 * or simply:    
``` 
python -m bot.main  
 ```
 * for Production:    
``` 
python -m bot.main --env prod
 ``` 

To run tests use this command      
``` pytest ```

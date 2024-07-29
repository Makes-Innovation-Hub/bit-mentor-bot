import argparse
import os
import sys

from dotenv import load_dotenv


class Config:
    def __init__(self, env: str):
        self.env = env
        self.load_environment()
        self.SERVER_URL = ""
        self.BOT_TOKEN = ""
        self.set_parameters()

    def load_environment(self):
        if self.env == 'prod':
            load_dotenv('.env_prod')
            print("Loaded environment variables from .env_prod")

        else:
            load_dotenv('.env_dev')
            print("Loaded environment variables from .env_dev")

    def set_parameters(self):
        if self.env == 'prod':
            self.SERVER_URL = os.getenv("SERVER_URL_PROD")
            self.BOT_TOKEN = os.getenv("BOT_TOKEN_PROD")
        else:
            self.SERVER_URL = os.getenv("SERVER_URL_DEV")
            self.BOT_TOKEN = os.getenv("BOT_TOKEN_DEV")

        if self.SERVER_URL is None or self.BOT_TOKEN is None:
            raise EnvironmentError(f"Environment variable  not found")


try:
    parser = argparse.ArgumentParser(description="Configuration")
    parser.add_argument('--env', default='dev', choices=['dev', 'prod'], help="Specify the environment (dev or prod)")
    args = parser.parse_args()
    config = Config(args.env)
    print(config.SERVER_URL, config.BOT_TOKEN)
except EnvironmentError as e:
    print(e)

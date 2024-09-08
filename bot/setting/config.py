import argparse
import os

from dotenv import load_dotenv
class Config:
    def __init__(self, env: str):
        """
        Initializes a new instance of the Config class.

        Args:
            env (str): The environment to configure for. Can be either 'prod' or 'dev'.
        """
        self.env = env
        self.SERVER_URL = ""
        self.BOT_TOKEN = ""
        self.GOOGLE_TIMEZONE = ""
        self.load_environment()
        self.set_parameters()

    def load_environment(self):
        """
        Load the environment variables based on the current environment.

        This function checks the current environment and loads the corresponding environment file.
        It first constructs the file path based on the environment. If the file exists, it loads the
        environment variables using the `load_dotenv` function. If the environment is 'prod', it
        loads the variables from '.env_prod' and prints a message. Otherwise, it loads the
        variables from '.env_dev' and prints a message.

        If the environment file is not found, a `FileNotFoundError` is raised.

        Raises:
            FileNotFoundError: If the environment file is not found.
        """
        filepath = '.env_prod' if self.env == 'prod' else '.env_dev'
        print(filepath)
        if os.path.exists(filepath):
            if self.env == 'prod':
                load_dotenv('.env_prod')
                print("Loaded environment variables from .env_prod")

            else:
                load_dotenv('.env_dev')
                print("Loaded environment variables from .env_dev")
        else:
            raise FileNotFoundError(f"Environment file '{filepath}' not found.")

    def set_parameters(self):
        """
        Sets the server URL, bot token, and Google timezone based on the current environment.
        
        If the environment is 'prod', it sets the parameters from the 'SERVER_URL_PROD', 'BOT_TOKEN_PROD', and 'GOOGLE_TIMEZONE_PROD' environment variables.
        If the environment is 'dev', it sets the parameters from the 'SERVER_URL_DEV', 'BOT_TOKEN_DEV', and 'GOOGLE_TIMEZONE_DEV' environment variables.
        
        Raises:
            EnvironmentError: If the 'SERVER_URL' or 'BOT_TOKEN' environment variable is not found.
        
        Returns:
            None
        """
        if self.env == 'prod':
            self.SERVER_URL = os.getenv("SERVER_URL_PROD")
            self.BOT_TOKEN = os.getenv("BOT_TOKEN_PROD")
            self.GOOGLE_TIMEZONE = os.getenv("GOOGLE_TIMEZONE_PROD")
        else:
            self.SERVER_URL = os.getenv("SERVER_URL_DEV")
            self.BOT_TOKEN = os.getenv("BOT_TOKEN_DEV")
            self.GOOGLE_TIMEZONE = os.getenv("GOOGLE_TIMEZONE_DEV")

        if self.SERVER_URL is None or self.BOT_TOKEN is None:
            raise EnvironmentError(f"Environment variable  not found")


try:
    parser = argparse.ArgumentParser(description="Configuration")
    parser.add_argument('--env', default='dev', choices=['dev', 'prod'], help="Specify the environment (dev or prod)")
    args, unknown = parser.parse_known_args()
    #args = parser.parse_args()
    config = Config(args.env)

except FileNotFoundError as e:
    print(e)
    exit(1)

except EnvironmentError as e:
    print(e)
    exit(1)

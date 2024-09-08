from bot.config.logging_config import app_logger

def test_logging():
    # Log some test messages
    app_logger.info("This is an info message for testing.")
    app_logger.error("This is an error message for testing.")

    # Verify that the log messages were written to the log file
    with open("logs/app.log", 'r') as f:
        log_contents = f.read()
        assert "This is an info message for testing." in log_contents
        assert "This is an error message for testing." in log_contents


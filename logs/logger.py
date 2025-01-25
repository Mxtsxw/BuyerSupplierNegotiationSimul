# logs/logger.py
class Logger:
    logs = []

    @staticmethod
    def log(message):
        Logger.logs.append(message)
        print(message)

    @classmethod
    def clear(cls):
        cls.logs = []
import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise Exception
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BASE_PORT = 5000
    DEBUG = False
    UPLOAD_FOLDER = "./app/text_files"
    FILE_FORMAT = "*.txt"


class Development(Config):
    DEBUG = True


class TestConfig(Config):
    DEBUG = True

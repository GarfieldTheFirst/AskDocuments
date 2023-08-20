import os
from app.utilities.getip import get_local_ip
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
    DB_NAME = os.environ.get('DB_NAME')
    # will create db in instance folder
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    BASE_PORT = 5000
    BASE_IP = 'http://' + get_local_ip() + ":{}".format(BASE_PORT)
    DEBUG = False
    UPLOAD_FOLDER = "./app/text_files"
    FILE_FORMAT = "*.txt"


class Development(Config):
    DEBUG = True


class TestConfig(Config):
    DEBUG = True
    DB_NAME = "database_test.db"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config

logger = logging.getLogger(__name__)
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    if not app.debug:
        # Setup logfile
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ordertrackingapp.log',
                                           maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: \
                %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.CRITICAL)
        logger.info('Order tracking app startup')
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.info('Order tracking app startup')
    app.config.from_object(config_class)
    bootstrap.init_app(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    from app.home import bp as home_bp

    app.register_blueprint(home_bp, url_prefix="/")

    return app

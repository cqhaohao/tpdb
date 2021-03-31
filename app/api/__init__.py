from api.config import configs
from flask import Flask, current_app
import logging
from logging.handlers import RotatingFileHandler


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    create_log(config_name)
    return app


def create_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=configs[config_name].LOGGING_DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("api/logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask api使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

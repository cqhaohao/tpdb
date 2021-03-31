class Config:
    DEBUG = False
    SECRET_KEY = 'app'


class DevConfig(Config):
    SCHEDULER_API_ENABLED = True
    LOGGING_DEBUG = 'DEBUG'
    DEBUG = True


class ProductionConfig(Config):
    SCHEDULER_API_ENABLED = True
    LOGGING_DEBUG = 'WARN'
    DEBUG = False


configs = {
    'dev': DevConfig,
    'production': ProductionConfig
}

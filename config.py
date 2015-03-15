import os
_basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    DATABASE_CONNECT_OPTIONS = {}
    THREADS_PER_PAGE = 8
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "somethingimpossibletoguess"
    #RECAPTCHA_USE_SSL = False
    #RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
    #RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
    #RECAPTCHA_OPTIONS = {'theme': 'white'}
    #MAIL_SERVER = 'smtp.googlemail.com'
    #MAIL_PORT = 587
    #MAIL_USE_TLS = True
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:111222@localhost/coffeehack'
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:111222@localhost/coffeehack'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        '''
        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
        '''

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

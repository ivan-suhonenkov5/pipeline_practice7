import os


class Config(object):
    APPNAME = "app"
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = "/static/upload/"
    SERVER_PATH = ROOT + UPLOAD_PATH

    USER = os.environ.get("POSTGRES_USER", "postgres")
    PASSWORD = os.environ.get("POSTGRES_PASSWORD", "1234")
    HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    PORT = os.environ.get("POSTGRES_PORT", "5432")
    DB = os.environ.get("POSTGRES_DB", "school")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:1234@127.0.0.1:5432/school'
    SECRET_KEY = "hfjsdkflsdfkjsdhfsdf3"
    SQLALCHEMY_TRACK_MODIFICATIONS = "True"

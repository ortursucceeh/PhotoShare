import cloudinary
import qrcode
from pydantic import BaseSettings


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)


def init_cloudinary():
    cloudinary.config(
        # cloud_name = settings.cloudinary_name,
        # api_key = settings.cloudinary_api_key,
        # api_secret = settings.cloudinary_api_secret,
        # secure = True
        cloud_name = "dybgf2pue",
        api_key = "461755645915968",
        api_secret = "rKEKisaiWSO6Bxe8RBHP-9dBE7I",
        secure = True
    )


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://ccawclzf:zZdgjAxqRfB3-Nc9DFCqlyyv1WvZqjVK@snuffleupagus.db.elephantsql.com:5432/ccawclzf'
    # sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@localhost:5432/postgres'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    mail_username: str = "example@meta.ua"
    mail_password: str = "secretPassword"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = "localhost"
    redis_port: int = 6379
    cloudinary_name: str = 'name'
    cloudinary_api_key: int = 5555555555555555
    cloudinary_api_secret: str = 'secret'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

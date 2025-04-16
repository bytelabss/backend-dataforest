import importlib.util
import logging
import importlib
import pkgutil

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from pymongo import MongoClient

from .config import Config

mongo_client = MongoClient(Config.MONGO_URI, document_class=dict)
mongo_db = mongo_client[Config.MONGO_DB]

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI, echo=Config.SQLALCHEMY_ECHO, plugins=["geoalchemy2"]
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def load_models():
    for module_info in pkgutil.iter_modules([Config.APP_DIR]):
        module_name = module_info.name
        if module_name in ["config", "database", "log", "blueprints"]:
            continue
        module_path = f"{Config.APP_MODULE}.{module_name}.models"
        if importlib.util.find_spec(module_path):
            logging.info(f"Loading models from [violet]{module_path}[/]")
            importlib.import_module(module_path)

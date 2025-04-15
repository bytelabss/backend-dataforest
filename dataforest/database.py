import importlib.util
import logging
import importlib
import pkgutil

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import Config


engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI, echo=Config.SQLALCHEMY_ECHO, plugins=["geoalchemy2"]
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# engine e session do secundário
secondary_engine = create_engine(
    Config.SQLALCHEMY_BINDS["secundario"], echo=Config.SQLALCHEMY_ECHO
)
SecondarySession = sessionmaker(autocommit=False, autoflush=False, bind=secondary_engine)

class Base(DeclarativeBase):
    pass

class SecondaryBase(DeclarativeBase):
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

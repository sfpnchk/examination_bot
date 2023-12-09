import os
import pathlib
from typing import Any

from yaml import CLoader as Loader
from yaml import load


class SingLetonBaseClass(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(SingLetonBaseClass, cls).__call__(
                *args, **kwargs
            )
        return cls._instance[cls]


class Config(metaclass=SingLetonBaseClass):

    config = {}

    @classmethod
    def load_config(cls, path: str):
        root_dir = pathlib.Path(__file__).parent.parent
        config_path = root_dir.joinpath(path or "bot/config.yaml")

        with open(config_path, "r") as config_file:
            cls.config = load(config_file, Loader=Loader)

        # setup for alembic support
        os.environ["database_uri"] = str(cls.config.get("database_uri"))
        return cls.config

    @classmethod
    def get_config(cls) -> dict:
        return cls.config

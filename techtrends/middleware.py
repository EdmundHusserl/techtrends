import logging
from functools import wraps
from dataclasses import (
    dataclass,
    field
)
from typing import (
    List,
    TextIO
)


@dataclass
class AppLogger:
    """
    Logging middleware instance used as an arg for application factory.
    increment method allows to decorate DB handlers to keep track of posts 
        and connections count. 
    """
    name: str
    level: int
    stream: List[TextIO]
    post_count: int = 0
    db_connection_count: int = 0
    logger: logging.Logger = field(init=False)

    def __post_init__(self):
        self.logger = self.create_logger(self.name, self.level)

    def create_logger(self, name: str, level: int = 10) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        formatter = logging.Formatter(
            "%(name)s %(levelname)s %(asctime)s %(message)s"
        )
                
        for s in self.stream:
            handler = logging.StreamHandler(s)
            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def increment(self, *fields):
        def increment_attribute(func):
            @wraps(func)
            def wrapped_func(*args, **kwargs):
                res = func(*args, **kwargs)
                try:
                    for f in fields:
                        self.__setattr__(
                            str(f),
                            int(getattr(self, f)) + 1
                        )
                except AttributeError as e:
                    self.logger.warning(f"{e.args}")
                    pass
                return res
            return wrapped_func
        return increment_attribute

    def set_post_count(self, count: int):
        self.post_count = count

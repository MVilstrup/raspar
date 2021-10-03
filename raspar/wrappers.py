from functools import partial
import validators
from typing import Any
from raspar.errors import FieldGenerationError, RequiredFieldMissingError
from raspar.utils import url_maker

class FieldValidator:
    def __init__(self, func, dtype, required) -> None:
        self.func = func
        self.dtype = dtype 
        self.required = required
    
    def __call__(self, element) -> Any:
        result = None
        try:
            result = self.func(element)
        except Exception as expt:
            raise FieldGenerationError from expt

        if result is None:
            if self.required:
                raise RequiredFieldMissingError(self.func.__name__)
        else:
            result = self.dtype(result)

        return result
        

def field(dtype=None, required=False):
    def wrap(func):
        return FieldValidator(func, dtype, required)
    
    return wrap

class LinkGenerator:
    def __init__(self, func) -> None:
        self.func = func

    def __call__(self, element) -> Any:
        links = self.func(element)
        links = map(str, links)
        links = map(lambda link: url_maker(link, element.url), links)
        links = filter(validators.url, links)
        return list(links)


def follow(func):
    return LinkGenerator(func)
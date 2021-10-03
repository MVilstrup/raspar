from typing import Any, Optional
from dateutil.parser import parse
from raspar.errors import TypeConversionError
import inspect

class _Type:
    
    def __call__(self, value) -> Any:
        try:
            return self.dtype.to_native(value)
        except:
            raise TypeConversionError(value)

class _String(_Type):
    def __init__(self) -> None:
        super().__init__()
        from schematics.types import StringType
        self.dtype = StringType()

    def __call__(self, value) -> Any:
        if not isinstance(value, str):
            raise TypeConversionError(value)
        return super().__call__(value)

class _Int(_Type):
    def __init__(self) -> None:
        super().__init__()
        from schematics.types import IntType
        self.dtype = IntType()

    def __call__(self, value) -> Any:
        if not isinstance(value, int):
            raise TypeConversionError(value)
        return super().__call__(value)

class _Float(_Type):
    def __init__(self) -> None:
        super().__init__()
        from schematics.types import FloatType
        self.dtype = FloatType()

    def __call__(self, value) -> Any:
        if not isinstance(value, (float, int)):
            raise TypeConversionError(value)
        return super().__call__(value)

class _Boolean(_Type):
    def __init__(self) -> None:
        super().__init__()
        from schematics.types import BooleanType
        self.dtype = BooleanType()

    def __call__(self, value) -> Any:
        if not isinstance(value, bool):
            raise TypeConversionError(value)
        return super().__call__(value)

class _Date(_Type):
    def __init__(self) -> None:
        super().__init__()
        from schematics.types import DateType
        self.dtype = DateType()

    def __call__(self, value) -> Any:
        try:
            return parse(value).date()
        except Exception as exp:
            raise TypeConversionError from exp

class _DateTime(_Type):
    def __init__(self) -> None:
        super().__init__()
        from schematics.types import DateTimeType
        self.dtype = DateTimeType()

    def __call__(self, value) -> Any:
        try:
            return parse(value)
        except Exception as exp:
            raise TypeConversionError from exp

class _List(_Type):

    def __init__(self, child_type: Optional[_Type]=None) -> None:
        super().__init__()
        if child_type is not None:
            if not inspect.isclass(child_type) and not issubclass(type(child_type), _Type):
                raise ValueError(child_type)
            elif inspect.isclass(child_type) and not issubclass(child_type, Schema):
                raise ValueError(child_type)
            
        self.child_type = child_type
    
    def __getitem__(self, child_type):
        return _List(child_type)

    def __call__(self, value) -> Any:
        if not isinstance(value, (list, tuple)):
            raise TypeConversionError(value)
        
        if self.child_type:
            return [self.child_type(element) for element in value]
        else:
            return list(value)



class Schema(_Type):

    def __new__(cls, value) -> Any:
        if not isinstance(value, dict):
            raise TypeConversionError(value)

        fields = {name: getattr(cls, name) for name in dir(cls) if issubclass(type(getattr(cls, name)), _Type)}

        own_keys = set(fields.keys())
        input_keys = set(value.keys())

        if own_keys.difference(input_keys) or input_keys.difference(own_keys):
            raise TypeConversionError(value)
        
        return {name: fields[name](v) for name, v in value.items()}



String = _String()
Int = _Int()
Float = _Float()
Boolean = _Boolean()
Date = _Date()
DateTime = _DateTime()
List = _List()

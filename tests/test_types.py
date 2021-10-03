import types
from raspar.types import String, Int, Float, Boolean, Date, DateTime, List, Schema
import pytest
from raspar.errors import TypeConversionError
from datetime import datetime, date

def test_string_type():
    assert String("test") == "test"
    assert String("") == ""

    with pytest.raises(TypeConversionError):
        String(1)

    with pytest.raises(TypeConversionError):  
        String(None)

    with pytest.raises(TypeConversionError):
        String(1.1)

def test_int_type():
    assert Int(1) == 1

    with pytest.raises(TypeConversionError):
        Int("1")

    with pytest.raises(TypeConversionError):  
        Int(None)
        
    with pytest.raises(TypeConversionError):
        Int(1.1)

def test_float_type():
    assert Float(1.1) == 1.1
    assert Float(1) == 1.

    with pytest.raises(TypeConversionError):
        Float("1")

    with pytest.raises(TypeConversionError):  
        Float(None)
        

def test_boolean_type():
    assert Boolean(True) == True
    assert Boolean(False) == False

    with pytest.raises(TypeConversionError):
        Boolean("True")

    with pytest.raises(TypeConversionError):  
        Boolean(None)

    with pytest.raises(TypeConversionError):  
        Boolean(1)


def test_date_type():
    assert Date("1/1/2001") == date(year=2001, month=1, day=1)
    assert Date("1-1-2001") == date(year=2001, month=1, day=1)

    with pytest.raises(TypeConversionError):  
        Date(1)

    with pytest.raises(TypeConversionError):  
        Date("")

    with pytest.raises(TypeConversionError):  
        Date(None)

def test_datetime_type():
    assert DateTime("1/1/2001") == datetime(year=2001, month=1, day=1)
    assert DateTime("1-1-2001") == datetime(year=2001, month=1, day=1)

    with pytest.raises(TypeConversionError):  
        DateTime(1)

    with pytest.raises(TypeConversionError):  
        DateTime("")

    with pytest.raises(TypeConversionError):  
        DateTime(None)

def test_list_type_untyped():
    assert List([]) == []
    assert List([1]) == [1]
    assert List([""]) == [""]
    assert List(("", )) == [""]

def test_list_type_typed():
    assert List[String]([]) == []
    assert List[String](["cool"]) == ["cool"]

    with pytest.raises(TypeConversionError):  
        List[String]([1])

def test_schema():
    class Test(Schema):
        name = String
        age = Int
    
    Test({"name": "name", "age": 2}) == {"name": "name", "age": 2}

    with pytest.raises(TypeConversionError):  
        Test({"age": 2}) 

    with pytest.raises(TypeConversionError):  
        Test({"name": "name", "age": 2, "cool": "man"}) 

def test_nested_schema():
    class Test(Schema):
        name = String
        age = Int

    class Elements(Schema):
        data = List[Test]
    
    Elements({"data": [{"name": "name", "age": 2}]}) 

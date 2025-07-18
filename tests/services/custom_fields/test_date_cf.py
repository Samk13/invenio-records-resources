# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test ISODate and EDTF Custom Field."""

import pytest
from marshmallow import Schema, ValidationError

from invenio_records_resources.services.custom_fields import (
    EDTFDateStringCF,
    ISODateStringCF,
)
from invenio_records_resources.services.custom_fields.errors import (
    CustomFieldsInvalidArgument,
)


#
# ISODateCF
#
def test_isodatestring_mapping():
    cf = ISODateStringCF("name")
    assert cf.mapping == {"type": "date"}


def test_isodatestring_validate():
    cf = ISODateStringCF("name")
    schema = Schema.from_dict({"test": cf.field})()

    assert schema.load({"test": "1999-10-27"}) == {"test": "1999-10-27"}
    pytest.raises(ValidationError, schema.load, {"f": "2020/2021"})


def test_isodatestring_custom_field_cls_list():
    """Test that field_cls cannot be passed as kwarg."""

    class MyClass:
        pass

    with pytest.raises(CustomFieldsInvalidArgument):
        _ = ISODateStringCF("name", field_cls=MyClass, multiple=True)


#
# EDTFDateStringCF
#
def test_edtfdatestring_mapping():
    cf = EDTFDateStringCF("name")
    assert cf.mapping == {
        "type": "object",
        "properties": {
            "date": {"type": "keyword"},
            "date_range": {"type": "date_range"},
        },
    }


def test_edtfdatestring_validate():
    cf = EDTFDateStringCF("name")
    schema = Schema.from_dict({"test": cf.field})()

    assert schema.load({"test": "2020-09/2020-10"}) == {"test": "2020-09/2020-10"}
    assert schema.load({"test": "2020-01-01T10:00:00"}) == {
        "test": "2020-01-01T10:00:00"
    }

    pytest.raises(ValidationError, schema.load, {"test": "2020-09-21garbage"})
    # Not chronological
    pytest.raises(ValidationError, schema.load, {"test": "2021/2020"})
    # Invalid interval
    pytest.raises(
        ValidationError,
        schema.load,
        {"test": "2020-01-01T10:00:00/2020-02-01T10:00:00"},
    )


def test_edtfdatestring_custom_field_cls_list():
    """Test that field_cls cannot be passed as kwarg."""

    class MyClass:
        pass

    with pytest.raises(CustomFieldsInvalidArgument):
        _ = EDTFDateStringCF("name", field_cls=MyClass, multiple=True)


def test_edtfdatestring_multiple_dump():
    field_name = "test_multiple_edtf"
    cf = EDTFDateStringCF(field_name, multiple=True)

    # Test loading multiple valid values
    data = {"custom_fields": {field_name: ["2020-09/2020-10", "2021-01-01"]}}
    expected_output = {
        "custom_fields": {
            field_name: [
                {
                    "date": "2020-09/2020-10",
                    "date_range": {"gte": "2020-09-01", "lte": "2020-10-31"},
                },
                {
                    "date": "2021-01-01",
                    "date_range": {"gte": "2021-01-01", "lte": "2021-01-01"},
                },
            ]
        }
    }

    cf.dump(data)

    assert data == expected_output


def test_edtfdatestring_multiple_load():
    field_name = "test_multiple_edtf"
    cf = EDTFDateStringCF(field_name, multiple=True)

    # Test loading multiple valid values
    data = {
        "custom_fields": {
            field_name: [
                {
                    "date": "2020-09/2020-10",
                    "date_range": {"gte": "2020-09-01", "lte": "2020-10-31"},
                },
                {
                    "date": "2021-01-01",
                    "date_range": {"gte": "2021-01-01", "lte": "2021-01-01"},
                },
            ]
        }
    }
    expected_output = {"custom_fields": {field_name: ["2020-09/2020-10", "2021-01-01"]}}

    cf.load(data)

    assert data == expected_output

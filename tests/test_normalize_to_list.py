import pytest
import collections
from app.cluegame import normalize_to_list


@pytest.fixture
def generic_class_with_name():
    C = collections.namedtuple('C', 'name data')
    return C


@pytest.fixture
def single_object_with_name(generic_class_with_name):
    C = generic_class_with_name
    return C('My C', 'Testing')


@pytest.fixture
def other_object_with_name(generic_class_with_name):
    C = generic_class_with_name
    return C('My Other C', 'Testing')


@pytest.fixture
def list_containing_object(single_object_with_name):
    return [single_object_with_name]


@pytest.fixture
def list_not_containing_object(other_object_with_name):
    return [other_object_with_name]


@pytest.fixture
def longer_list_containing_object(single_object_with_name,
                                  other_object_with_name):
    return [single_object_with_name, other_object_with_name]


@pytest.fixture
def longer_list_containing_object_at_end(single_object_with_name,
                                         other_object_with_name):
    return [other_object_with_name, single_object_with_name]


def test_normalize_singleton(single_object_with_name, list_containing_object):
    obj = single_object_with_name
    lst = list_containing_object

    assert normalize_to_list(obj, lst).name == obj.name
    assert normalize_to_list(obj, lst) in lst


def test_missing(single_object_with_name, list_not_containing_object):
    obj = single_object_with_name
    lst = list_not_containing_object

    with pytest.raises(ValueError):
        normalize_to_list(obj, lst)


def test_nontrivial_list(single_object_with_name,
                         longer_list_containing_object):
    obj = single_object_with_name
    lst = longer_list_containing_object

    assert normalize_to_list(obj, lst).name == obj.name
    assert normalize_to_list(obj, lst) in lst


def test_list_with_object_at_end(single_object_with_name,
                                 longer_list_containing_object_at_end):
    obj = single_object_with_name
    lst = longer_list_containing_object_at_end

    assert normalize_to_list(obj, lst).name == obj.name
    assert normalize_to_list(obj, lst) in lst

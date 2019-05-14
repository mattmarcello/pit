import pytest
import os
import sys
import secrets
from pathlib import Path

sys.path.insert(0, "/Users/mpm/src/building_git")

from lib.index import Index


@pytest.fixture
def tmp_path():
    dirname = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(dirname, "..", "tmp"))


@pytest.fixture
def index_path(tmp_path):
    return os.path.join(tmp_path, "index")


@pytest.fixture
def index(index_path):
    return Index(index_path)


@pytest.fixture
def stat():
    return os.stat(__file__)


@pytest.fixture
def oid():
    return secrets.token_hex(20)


def test_adds_a_single_file(index, stat, oid):
    """TODO should we need to create path objects here  ?"""
    index.add(Path("alice.txt"), oid, stat)
    assert ["alice.txt"] == list(
        map(lambda entry: entry.path.decode("utf-8"), index.get_entries())
    )

def test_replaces_a_file_with_a_directory(oid, stat, index):

    index.add(Path("alice.txt"), oid, stat)
    index.add(Path("bob.txt"), oid, stat)

    index.add(Path("alice.txt/nested.txt"), oid, stat)

    assert ["alice.txt/nested.txt", "bob.txt"] == list(
        map(lambda entry: entry.path.decode("utf-8"), index.get_entries())
    )

def test_replaces_a_directory_with_a_file(oid, stat, index):
    index.add(Path("alice.txt"), oid, stat)
    index.add(Path("nested/bob.txt"), oid, stat)

    index.add(Path("nested"), oid, stat)

    assert ["alice.txt", "nested"] == list(
        map(lambda entry: entry.path.decode("utf-8"), index.get_entries())
    )


def test_recursively_replaced_a_directory_with_a_file(oid, stat, index):
    index.add(Path("alice.txt"), oid, stat)
    index.add(Path("nested/bob.txt"), oid, stat)
    index.add(Path("nested/inner/claire.txt"), oid, stat)

    index.add(Path("nested"), oid, stat)

    assert ["alice.txt", "nested"] == list(
        map(lambda entry: entry.path.decode("utf-8"), index.get_entries())
    )











pytest.ini
[pytest]
addopts = -v
testpaths = test

test/test_hello_world.py
def test_hello_world():
    assert 1 + 1 == 2
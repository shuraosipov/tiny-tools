import programming_languages as pl

def test_python_resources():
    python = pl.Python()
    assert python.display_resources() == 'Python resources: Tutorial, Examples, Tips'

def test_java_resources():
    java = pl.Java()
    assert java.display_resources() == 'Java resources: Tutorial, Examples, Tips'
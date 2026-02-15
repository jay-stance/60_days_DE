def test_true():
  assert(True)
  
def test_false():
  assert(False)
  
import pytest
  
@pytest.fixture
def example_fixture():
  return 'jay'

def test_with_fixtures(example_fixture):
  assert example_fixture == 'jay'
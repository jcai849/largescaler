import pytest
from largescaler import Local, Master, Run


@pytest.fixture
def run():
    return Run(type="lasso")


def test_master_kdl(run: Run):
    m = Master(run, 1234)
    m.to_kdl()

@pytest.fixture
def local(run: Run):
    return Local(run, 20)

def test_local_kdl(local: Local):
    local.exec()

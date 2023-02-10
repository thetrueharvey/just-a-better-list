'''Fixtures for testing
'''
# %% Libraries
# stdlib
from enum import Enum

# 3rd party
from pytest import fixture

# module

# %% Configuration
class Scope(Enum):
    Session = 'session'
    Module = 'module'
    Function = 'function'

    def __repr__(self):
        return self.value

# %%
@fixture(scope=Scope.Session.value)
def simple_data():
    yield [1, 2, 3, 4, 5] 

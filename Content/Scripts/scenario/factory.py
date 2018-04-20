from scenario import O1
from scenario import sandbox

train_classes = {
    'O1': O1.O1Train,
    'SandBox': sandbox.SandBox}


test_classes = {
    'O1': O1.O1Test,
    'SandBox': sandbox.SandBox}


def get_train_scenario(name, world):
    return train_classes[name](world)


def get_test_scenario(name, world):
    return test_classes[name](world)

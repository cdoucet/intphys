from scenario import O1
from scenario import sandbox

train_classes = {
    'O1': O1.O1Train,
    'SandBox': sandbox.SandBox}


test_classes = {
    'O1': O1.O1TestStatic,
    'SandBox': sandbox.SandBox}


def get_train_scenario(name):
    return train_classes[name]()


def get_test_scenario(name, is_occluded=False, is_static=True, ntricks=1):
    return test_classes[name](
        is_occluded=is_occluded,
        is_static=is_static,
        ntricks=ntricks)

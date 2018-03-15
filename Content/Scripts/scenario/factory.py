from scenario import O1


train_classes = {
    'O1': O1.O1Train}


test_classes = {
    'O1': O1.O1Test}


def get_train_scenario(name):
    return train_classes[name]()


def get_test_scenario(name, is_occluded=False, is_static=True, ntricks=1):
    return test_classes[name](
        is_occluded=is_occluded,
        is_static=is_static,
        ntricks=ntricks)

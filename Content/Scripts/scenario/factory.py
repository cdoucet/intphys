from scenario import O1

def get_train_scenario(name):
    scenarii = {
        'O1': O1.O1Train
    }

    return scenarii[name]()

def get_test_scenario(name, is_occluded=False, is_static=True, ntricks=1):
    scenarii = {
        'O1': O1.O1Test
    }

    return scenarii[name](
        is_occluded=is_occluded,
        is_static=is_static,
        ntricks=ntricks)

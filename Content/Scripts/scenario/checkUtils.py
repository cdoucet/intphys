import unreal_engine as ue


def checks_time_laps(check_array, desired_bool):
    # check_array can either be an
    # array of both runs or an array of one run
    # we are looking for the desired bool in this/these array(s)
    res = []
    if len(check_array) == 2:
        if len(check_array[0]) == len(check_array[1]):
            nb = len(check_array[0])
        else:
            ue.log_warning("run's arrays size don't match")
            return res
    else:
        nb = len(check_array)
    for frame in range(nb):
        if (len(check_array) == 2 and check_array[0][frame] ==
                check_array[1][frame] and
                check_array[1][frame] == desired_bool):
            res.append(frame)
        elif len(check_array) > 2 and check_array[frame] == desired_bool:
            res.append(frame)
    return res


def remove_invisible_frames(array):
    # remove the last occurences of not visible actor if
    # it is out of the fieldview
    first = 0
    last = 99
    while True:
        quit = False
        if array[0] == first:
            array.remove(first)
            first += 1
        else:
            quit = True
        if array[-1] == last:
            array.remove(last)
            last -= 1
        elif quit is True:
            break
    return array


def remove_last_and_first_frames(array, nb_frames):
    for frame in range(nb_frames):
        array.remove(array[0])
        array.remove(array[-1])
    return array


def separate_period_of_occlusions(array):
    i = 0
    occlusion = []
    occlusion.append([])
    previous_frame = array[0] - 1
    # distinguish the different occlusion time laps
    for frame in array:
        if frame - 1 != previous_frame:
            i += 1
            occlusion.append([])
        occlusion[i].append(frame)
        previous_frame = frame
    # if there is less than 2 distinct occlusion the scene will restart
    if (len(occlusion) < 2 or
            len(occlusion[0]) == 0 or
            len(occlusion[1]) == 0):
        ue.log_warning("not enough occluded frame")
        raise IndexError()
    return occlusion


def remove_frame_after_first_bounce(array):
    previous = array[0]
    delete = False
    temp_array = array
    for frame in array:
        if delete is True:
            temp_array.remove(frame)
            continue
        if frame != previous + 1:
            delete = True
    return temp_array

def store_actors_locations(actors):


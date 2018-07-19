from unreal_engine import FVector, FRotator
import unreal_engine as ue


# check_array can either be an
# array of both runs or an array of one run
# we are looking for the desired bool in this/these array(s)
def checks_time_laps(check_array, desired_bool):
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


# currently used in each dynamic scene to
# make sure the magic tick doesn't happen when the actor is hidden
# remove the last occurences of not visible actor if
# it is invisible
def remove_invisible_frames(visibility_array):
    first = 0
    last = 99
    while True:
        quit = False
        if visibility_array[0] == first:
            visibility_array.remove(first)
            first += 1
        else:
            quit = True
        if visibility_array[-1] == last:
            visibility_array.remove(last)
            last -= 1
        elif quit is True:
            break
    return visibility_array


# used to make sure that the magic tick doesn't happen too soon or
# too late in the scene, making it hard to see
def remove_last_and_first_frames(visibility_array, nb_frames):
    for frame in range(nb_frames):
        visibility_array.remove(visibility_array[0])
        visibility_array.remove(visibility_array[-1])
    return visibility_array


# currently used exclusively in dynamic 2 occluded to make sure
# each magic tick happen between a different occluder
def separate_period_of_occlusions(visibility_array):
    i = 0
    occlusion_periods = []
    occlusion_periods.append([])
    previous_frame = visibility_array[0] - 1
    # distinguish the different occlusion time laps
    for frame in visibility_array:
        if frame - 1 != previous_frame:
            i += 1
            occlusion_periods.append([])
        occlusion_periods[i].append(frame)
        previous_frame = frame
    # if there is less than 2 distinct occlusion the scene will restart
    if (len(occlusion_periods) < 2 or
            len(occlusion_periods[0]) == 0 or
            len(occlusion_periods[1]) == 0):
        ue.log_warning("not enough occluded frame")
        raise IndexError()
    return occlusion_periods


# currently used in O2 exclusively to make the magic tick happen
# before the object bounce on the ground
def remove_frame_after_first_bounce(grounded_array):
    previous = grounded_array[0]
    delete = False
    temp_array = grounded_array
    for frame in grounded_array:
        if delete is True:
            temp_array.remove(frame)
            continue
        if frame != previous + 1:
            delete = True
    return temp_array


# used for visible dynamic 2, this function take a (magic_tick_frame) in
# parameter and remove the (nb_frame) adjacent frames in the (array)
def remove_frames_close_to_magic_tick(array, magic_tick_frame, frame_nb):
    a = 0
    b = 0
    array.remove(magic_tick_frame)
    for i in range(5):
        try:
            array.remove(magic_tick_frame - (i + 1))
            a += 1
        except ValueError:
            if magic_tick_frame - (i + 1) != array[0]:
                a += 1
        try:
            array.remove(magic_tick_frame + (i + 1))
            b += 1
        except ValueError:
            if magic_tick_frame + (i + 1) != array[-1]:
                b += 1
    if a != 5 and b != 5:
        raise IndexError()
    return array


# we check if the location and rotation
# of each object is the same at each run during the magic tick
def store_actors_locations(actors):
    result = []
    for name, actor in actors.items():
        result.append([])
        result[-1].append(FVector())
        result[-1][0].x = int(round(actor.actor.get_actor_location().x))
        result[-1][0].y = int(round(actor.actor.get_actor_location().y))
        result[-1][0].z = int(round(actor.actor.get_actor_location().z))
        result[-1].append(FRotator())
        result[-1][1].yaw = int(round(actor.actor.get_actor_rotation().yaw))
        result[-1][1].roll = int(round(actor.actor.get_actor_rotation().roll))
        result[-1][1].pitch = \
            int(round(actor.actor.get_actor_rotation().pitch))
    return result

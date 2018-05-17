# O4 Scenario

## Abstract

The O4 scenario is about Energy and momentum.

## Physical principles

Constant kinetic energy and momentum.

## Computational challenge

Tracking/predicting object trajectories.

## General description

### Train

* Every train sequence are possible.
* One run in each train scene.
* From 1 to 3 actors per scene.
* From 0 to 2 occluders.
* Random locations and rotations of actors and occluders.
* Random forces applied to actors.
* Random textures are applied to the floor, the occluders and the actors
* Occluders movements are random and sporadic.
* Actors can only be spheres.

![Scene](Train/scene/video.gif)
![Depth](Train/depth/video.gif)
![Mask](Train/masks/video.gif)

### Test

* Four runs in each test scene.
* From 1 to 3 actors per scene.
* Actors can only be spheres.
* Random textures are applied to the floor, the occluders and the actors.

#### Visible

* No occluders.

##### Static

* The actor(s) do(es)n't move at the start.

###### Possible 1

![scene](Test/visible/static/1/scene/video.gif)
![depth](Test/visible/static/1/depth/video.gif)
![mask](Test/visible/static/1/masks/video.gif)

###### Possible 2

![scene](Test/visible/static/2/scene/video.gif)
![depth](Test/visible/static/2/depth/video.gif)
![mask](Test/visible/static/2/masks/video.gif)

###### Impossible 1

* One actor spawns and then rolls away.

![scene](Test/visible/static/3/scene/video.gif)
![depth](Test/visible/static/3/depth/video.gif)
![mask](Test/visible/static/3/masks/video.gif)

###### Impossible 2

* One actor spawns (but at a different place than the previous run) and then rolls away.

![scene](Test/visible/static/4/scene/video.gif)
![depth](Test/visible/static/4/depth/video.gif)
![mask](Test/visible/static/4/masks/video.gif)

##### Dynamic 1

* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/visible/dynamic_1/1/scene/video.gif)
![depth](Test/visible/dynamic_1/1/depth/video.gif)
![mask](Test/visible/dynamic_1/1/masks/video.gif)

###### Possible 2

![scene](Test/visible/dynamic_1/2/scene/video.gif)
![depth](Test/visible/dynamic_1/2/depth/video.gif)
![mask](Test/visible/dynamic_1/2/masks/video.gif)

###### Impossible 1

* One actor spawns and then changes trajectory at a random frame.

![scene](Test/visible/dynamic_1/3/scene/video.gif)
![depth](Test/visible/dynamic_1/3/depth/video.gif)
![mask](Test/visible/dynamic_1/3/masks/video.gif)

###### Impossible 2

* One actor spawns (but at a different place than the previous run) and then changes trajectory at a random frame.

![scene](Test/visible/dynamic_1/4/scene/video.gif)
![depth](Test/visible/dynamic_1/4/depth/video.gif)
![mask](Test/visible/dynamic_1/4/masks/video.gif)

##### Dynamic 2

* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/visible/dynamic_2/1/scene/video.gif)
![depth](Test/visible/dynamic_2/1/depth/video.gif)
![mask](Test/visible/dynamic_2/1/masks/video.gif)

###### Possible 2

![scene](Test/visible/dynamic_2/2/scene/video.gif)
![depth](Test/visible/dynamic_2/2/depth/video.gif)
![mask](Test/visible/dynamic_2/2/masks/video.gif)

###### Impossible 1

* One actor spawns, changes trajectory at a random frame, then changes it again.

![scene](Test/visible/dynamic_2/3/scene/video.gif)
![depth](Test/visible/dynamic_2/3/depth/video.gif)
![mask](Test/visible/dynamic_2/3/masks/video.gif)

###### Impossible 2

* One actor spawns, changes trajectory at a random frame, then changes it again.

![scene](Test/visible/dynamic_2/4/scene/video.gif)
![depth](Test/visible/dynamic_2/4/depth/video.gif)
![mask](Test/visible/dynamic_2/4/masks/video.gif)

#### Occluded

##### Static

* The occluder stands up then gets down.

###### Possible 1

![scene](Test/occluded/static/1/scene/video.gif)
![depth](Test/occluded/static/1/depth/video.gif)
![mask](Test/occluded/static/1/masks/video.gif)

###### Possible 2

![scene](Test/occluded/static/2/scene/video.gif)
![depth](Test/occluded/static/2/depth/video.gif)
![mask](Test/occluded/static/2/masks/video.gif)

###### Impossible 1

* One actor start moving when occluder is up.

![scene](Test/occluded/static/3/scene/video.gif)
![depth](Test/occluded/static/3/depth/video.gif)
![mask](Test/occluded/static/3/masks/video.gif)

###### Impossible 2

* One actor start moving when occluder is up.

![scene](Test/occluded/static/4/scene/video.gif)
![depth](Test/occluded/static/4/depth/video.gif)
![mask](Test/occluded/static/4/masks/video.gif)

##### Dynamic 1

* One occluder spawns, up, in the center of the scene.
* The occluder gets down.
* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/occluded/dynamic_1/1/scene/video.gif)
![depth](Test/occluded/dynamic_1/1/depth/video.gif)
![mask](Test/occluded/dynamic_1/1/masks/video.gif)

###### Possible 2

![scene](Test/occluded/dynamic_1/2/scene/video.gif)
![depth](Test/occluded/dynamic_1/2/depth/video.gif)
![mask](Test/occluded/dynamic_1/2/masks/video.gif)

###### Impossible 1

* One actor changes trajectory when going behind occluder.

![scene](Test/occluded/dynamic_1/3/scene/video.gif)
![depth](Test/occluded/dynamic_1/3/depth/video.gif)
![mask](Test/occluded/dynamic_1/3/masks/video.gif)

###### Impossible 2

* One actor changes trajectory when going behind occluder.

![scene](Test/occluded/dynamic_1/4/scene/video.gif)
![depth](Test/occluded/dynamic_1/4/depth/video.gif)
![mask](Test/occluded/dynamic_1/4/masks/video.gif)

##### Dynamic 2

* Two occluders spawn, up, at equal distances from the center of the scene.
* The occluders get down.
* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/occluded/dynamic_2/1/scene/video.gif)
![depth](Test/occluded/dynamic_2/1/depth/video.gif)
![mask](Test/occluded/dynamic_2/1/masks/video.gif)

###### Possible 2

![scene](Test/occluded/dynamic_2/2/scene/video.gif)
![depth](Test/occluded/dynamic_2/2/depth/video.gif)
![mask](Test/occluded/dynamic_2/2/masks/video.gif)

###### Impossible 1

* One actor changes trajectory when going behind each occluder.

![scene](Test/occluded/dynamic_2/3/scene/video.gif)
![depth](Test/occluded/dynamic_2/3/depth/video.gif)
![mask](Test/occluded/dynamic_2/3/masks/video.gif)

###### Impossible 2

* One actor changes trajectory when going behind each occluder.

![scene](Test/occluded/dynamic_2/4/scene/video.gif)
![depth](Test/occluded/dynamic_2/4/depth/video.gif)
![mask](Test/occluded/dynamic_2/4/masks/video.gif)

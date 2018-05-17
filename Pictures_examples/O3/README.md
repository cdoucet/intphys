# O3 Scenario

## Abstract

The O3 scenario is about Spatio-temporal continuity.

## Physical principles

Trajectories of objects are continuous.

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

![Scene](Train/video.gif)

### Test

* Four runs in each test scene.
* From 1 to 3 actors per scene.
* Actors can only be spheres.
* Random textures are applied to the floor, the occluders and the actors.

#### Visible

* No occluders.

##### Static

* The actor(s) do(es)n't move.

###### Possible 1

![scene](Test/visible/static/1/video.gif)

###### Possible 2

![scene](Test/visible/static/2/video.gif)

###### Impossible 1

* One actor spawns and then teleports somewhere else at a random frame.

![scene](Test/visible/static/3/video.gif)

###### Impossible 2

* One actor spawns and then teleports somewhere else at a random frame (but at a different place than the previous video).

![scene](Test/visible/static/4/video.gif)

##### Dynamic 1

* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/visible/dynamic_1/1/video.gif)

###### Possible 2

![scene](Test/visible/dynamic_1/2/video.gif)

###### Impossible 1

* One actor spawns and then teleports somewhere else at a random frame.

![scene](Test/visible/dynamic_1/3/video.gif)

###### Impossible 2

* One actor spawns and then teleports somewhere else at a random frame (but at a different place than the previous video).

![scene](Test/visible/dynamic_1/4/video.gif)

##### Dynamic 2

* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/visible/dynamic_2/1/video.gif)

###### Possible 2

![scene](Test/visible/dynamic_2/2/video.gif)

###### Impossible 1

* One actor spawns, teleports somewhere else at a random frame, then teleports again somewhere else.

![scene](Test/visible/dynamic_2/3/video.gif)

###### Impossible 2

* One actor spawns, teleports somewhere else at a random frame, then teleports again somewhere else.

![scene](Test/visible/dynamic_2/4/video.gif)

#### Occluded

##### Static

* The occluder stands up then gets down.

###### Possible 1

![scene](Test/occluded/static/1/video.gif)

###### Possible 2

![scene](Test/occluded/static/2/video.gif)

###### Impossible 1

* One actor changed location when occluder gets down.

![scene](Test/occluded/static/3/video.gif)

###### Impossible 2

* One actor changed location when occluder gets down.

![scene](Test/occluded/static/4/video.gif)

##### Dynamic 1

* One occluder spawns, up, in the center of the scene.
* The occluder gets down.
* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/occluded/dynamic_1/1/video.gif)

###### Possible 2

![scene](Test/occluded/dynamic_1/2/video.gif)

###### Impossible 1

* One actor teleports himself when going behind the occluder (the time it takes for it to go through an occluder is odd)

![scene](Test/occluded/dynamic_1/3/video.gif)

###### Impossible 2

* One actor teleports himself when going behind the occluder (the time it takes for it to go through an occluder is odd)

![scene](Test/occluded/dynamic_1/4/video.gif)

##### Dynamic 2

* Two occluders spawn, up, at equal distances from the center of the scene.
* The occluders get down.
* The actor(s) can either spawn at the left or the right of the scene.
* A force will apply to it/them, making it/them roll to the other side of the scene.

###### Possible 1

![scene](Test/occluded/dynamic_2/1/video.gif)

###### Possible 2

![scene](Test/occluded/dynamic_2/2/video.gif)

###### Impossible 1

* One actor teleports himself when going behind each occluder (the time it takes for it to go through an occluder is odd)

![scene](Test/occluded/dynamic_2/3/video.gif)

###### Impossible 2

* One actor teleports himself when going behind each occluder (the time it takes for it to go through an occluder is odd)

![scene](Test/occluded/dynamic_2/4/video.gif)

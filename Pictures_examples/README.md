# GENERAL PRESENTATION

## SCENARIOS

Each scenario has a physical principle which will be broken in impossible videos and a computational challenge which will be tested by eponym videos.

## VIDEO TYPES LEXICON

### TRAIN

Train videos are all possibles sequences.
They are much random.
There is one video per train scene.

### TEST

Tests videos are less random than the trains videos.
A single actor is chosen to be the magic actor.

#### There are 4 videos per test scene :

##### Some possible videos

ICI 4 VIDEOS POSSIBLES (SCENES DIFFERENTES, SEULEMENT LES RGB - PAS DE DEPTH OU MASKS). ON VA ENLEVER LES NOTIONS DE 1ST 2ND 3RD 4TH VIDEOS PARCE QUE ELLES SERONT MELANGEES ET C'EST PAS EVIDENT A COMPRENDS AU PREMIER ABORD.

##### Some impossible videos

ICI 4 VIDEOS IMPOSSIBLES (SCENES DIFFERENTES, SEULEMENT LES RGB - PAS DE DEPTH OU MASKS)

#### A test scene can be :

##### Visible

* There is no occluder in this one.
* The magic trick always occures when the magic actor is visible.

##### Occluded

* There is occluders in this one.
* The magic trick always occures when the magic actor is behind an occluder.

#### A test scene can be :

##### Static

* The actors don't move.
* If the scene is occluded, there is one occluder.
* The occluder (if present) can rotate.
* There is one magic trick.

##### Dynamic 1

* The actors move.
* If the scene is occluded, there is one occluder.
* The occluder (if present) can rotate.
* The actors can spawn either at the left or the right of the scene.
* The actors go alongside in the direction of the other side of the scene.
* There is one magic trick.

##### Dynamic 2

* The actors move.
* If the scene is occluded, there is two occluders.
* The occluder (if present) can rotate.
* The actors can spawn either at the left or the right of the scene.
* The actors go alongside in the direction of the other side of the scene.
* There is two magic tricks.

## OBJECTS LEXICON

### Actor

* An actor can be a sphere, a cube or a cone from differents textures.
* Forces can be applied to them in trains or dynamic tests.
* In tests videos, a magic actor will be chosen among all the actors.
* They submit to the physic laws.

### Occluder

* An occluder is a rectangle which can spawn either up or down.
* It will stand up and go down during video.
* Movement speed can change.
* It can spawn in occluded tests or trains.
* In occluded test video, it will hides the magic trick.
* They don't submit to physic laws.

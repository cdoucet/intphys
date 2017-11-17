"""Main script interacting at world level with UE

This module is attached to the MainPythonComponant PyActor in UE.

"""

import unreal_engine as ue
import screenshot
import importlib
importlib.reload(screenshot)
from unreal_engine import FVector, FRotator
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize

# the default screen resolution (in pixels)
width, height = 288, 288


ue.log('#' * 50)
ue.log('Beginning new game')

uclass = {'PhysicsObject': ue.load_class('/Game/PhysicsObject.PhysicsObject_C')}


class MainPythonComponant:
    def get_resolution(self):
        return str(width) + 'x' + str(height)

    def print_tick(self, delta_seconds):
        ue.log('ticking after {}'.format(float(delta_seconds)))
        print(ue.get_viewport_screenshot() == None)

    def begin_play(self):
        self.world = self.uobject.get_world()
        ue.log('Raising new world {}'.format(self.world.get_name()))

        # spawn a new PyActor
        self.new_actor = self.world.actor_spawn(
            uclass['PhysicsObject'],
            FVector(300, 0, 50),
            FRotator(0, 0, 0))
        self.camera = screenshot.getCamera(self.new_actor)

    def tick(self, delta_time): # put the screenshot screen in the begin play make the size of the screenshot wrong
        size = IntSize(288, 288) # this line let size.X and size.Y with a null value... can't say why
        size.X = 288
        size.Y = 288
        array = []
        array.append(self.new_actor)
        array2 = []
        #if screenshot.takeDepth(size, 1, self.camera, array, array2) == False:
            #print("depth failed")

        if screenshot.takeScreenshot(size) == False:
            print("screenshot failed")


        #array = []
        #array.append(new_actor)
        #array2 = []
        #camera = testScreenshot.GetCamera(self.world)
        #camera = ue.find_object('/Game/UEDPIE_0_TestMap.TestMap:PersistentLevel.Camera_81')
        #screenshot.doTheWholeStuff(IntSize(288, 288), 1, camera, array, array2)
        #screenshot.salut()
        
        # # add a sphere component as the root one
        # static_mesh = new_actor.add_actor_root_component(
        #     ue.find_class('StaticMeshComponent'), 'SphereMesh')
        # ue.log(static_mesh)

        # # set the mesh as the Sphere asset
        # static_mesh.call('SetStaticMesh /Engine/EngineMeshes/Sphere.Sphere')
        # # # set the python module
        # # new_actor.set_property('PythonModule', 'mobile_object')
        # # # set the python class
        # # new_actor.set_property('PythonClass', 'MobileObjectPythonComponant')

        # new_actor.bVisible = True

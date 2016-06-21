local uetorch = require 'uetorch'
local block = {}

local sphere = uetorch.GetActor("Sphere_4")
local wall = uetorch.GetActor("Wall_400x200_8")
block.actors = {sphere=sphere, wall=wall}

local camera = uetorch.GetActor("MainMap_CameraActor_Blueprint_C_0")

local sphere_visible = true
local t_rotation = 0
local t_rotation_change = 0

local function WallRotationDown(dt)
	local angle = (t_rotation - t_rotation_change) * 20
	uetorch.SetActorRotation(wall, 0, 0, angle)
	if angle >= 90 then
		uetorch.RemoveTickHook(WallRotationDown)
		t_rotation_change = t_rotation
	end
	t_rotation = t_rotation + dt
end

local function WallRotationUp(dt)
	local angle = (t_rotation - t_rotation_change) * 20
	uetorch.SetActorRotation(wall, 0, 0, 90 - angle)
	if angle >= 90 then
		uetorch.RemoveTickHook(WallRotationUp)
		uetorch.AddTickHook(WallRotationDown)
		t_rotation_change = t_rotation

		if math.random(2) == 1 then
			sphere_visible = true
		else
			sphere_visible = false
		end
		uetorch.SetActorVisible(sphere, sphere_visible)
	end
	t_rotation = t_rotation + dt
end

function block.set_block()
	uetorch.AddTickHook(WallRotationUp)
	uetorch.SetActorLocation(camera, 100, 30, 80)
	uetorch.SetActorLocation(wall, -100, -350, 20)
	uetorch.SetActorLocation(sphere, 150, -550, 70)
	uetorch.SetActorVisible(sphere, sphere_visible)
end

return block
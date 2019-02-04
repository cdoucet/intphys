// Fill out your copyright notice in the Description page of Project Settings.

#include "Friction.h"
#include "Runtime/Engine/Classes/PhysicalMaterials/PhysicalMaterial.h"
#include "Runtime/Core/Public/GenericPlatform/GenericPlatformMisc.h"

bool UFriction::SetFriction(UMaterial* Material, float &Friction)
{
    UPhysicalMaterial *PhysicalMaterial = Material->GetPhysicalMaterial();
    if (PhysicalMaterial == nullptr)
    {
        return false;
    }
    PhysicalMaterial->Friction = Friction;
    PhysicalMaterial->UpdatePhysXMaterial();
    return true;
}

bool UFriction::SetRestitution(UMaterial* Material, float &Restitution)
{
    UPhysicalMaterial* PhysicalMaterial = Material->GetPhysicalMaterial();
    if (PhysicalMaterial == nullptr)
    {
        return false;
    }
    PhysicalMaterial->Restitution = Restitution;
    PhysicalMaterial->UpdatePhysXMaterial();
    return true;
}

void    UFriction::ExitEngine(bool force)
{
	FGenericPlatformMisc::RequestExit(force);
}

void	UFriction::SetMassScale(UStaticMeshComponent* Component, float MassScale)
{
    if(!Component) return;
    FBodyInstance* BodyInst = Component->GetBodyInstance();
    if(!BodyInst) return;
    BodyInst->MassScale = MassScale;
    BodyInst->UpdateMassProperties();
}

bool UFriction::SetVelocity(AActor *Actor, FVector Velocity)
{
    if (Actor == nullptr)
    {
        return false;
    }
    Actor->GetRootComponent()->ComponentVelocity = Velocity;
    return true;
}

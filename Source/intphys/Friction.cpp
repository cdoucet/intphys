// Fill out your copyright notice in the Description page of Project Settings.

#include "Friction.h"
#include "Runtime/Engine/Classes/PhysicalMaterials/PhysicalMaterial.h"


bool UFriction::SetFriction(UMaterial* Material, float Friction)
{
    UPhysicalMaterial* PhysicalMaterial = Material->GetPhysicalMaterial();
    if (PhysicalMaterial == nullptr)
    {
        return false;
    }

    PhysicalMaterial->Friction = Friction;
    PhysicalMaterial->RebuildPhysicalMaterials();
    PhysicalMaterial->UpdatePhysXMaterial();

    return true;
}

bool UFriction::SetRestitution(UMaterial* Material, float restitution)
{
    UPhysicalMaterial* PhysicalMaterial = Material->GetPhysicalMaterial();
    if (PhysicalMaterial == nullptr)
    {
        return false;
    }
    PhysicalMaterial->Restitution = restitution;
    PhysicalMaterial->RebuildPhysicalMaterials();
    PhysicalMaterial->UpdatePhysXMaterial();

    return true;
}

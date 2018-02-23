// Fill out your copyright notice in the Description page of Project Settings.

#include "Friction.h"


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

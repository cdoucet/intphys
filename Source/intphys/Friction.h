// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Friction.generated.h"

/**
 *
 */
UCLASS()
class INTPHYS_API UFriction : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFONCTION(BlueprintCallable, Category="IntPhys")
    static bool SetFriction(UMaterial* Material, float Friction);
};

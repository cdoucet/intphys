// Copyright 2016, 2017 Mario Ynocente Castro, Mathieu Bernard.

#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "NaivePhysicsLib.generated.h"

/**
 *
 */
UCLASS()
class NAIVEPHYSICS_API UNaivePhysicsLib : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

    UFUNCTION(BlueprintCallable, Category="Naive Physics Lib")
    static UMaterialInterface* GetMaterial(const FString& Name);
};

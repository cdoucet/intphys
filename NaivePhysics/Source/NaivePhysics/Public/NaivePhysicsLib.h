// Fill out your copyright notice in the Description page of Project Settings.

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

public:
        UFUNCTION(BlueprintCallable, Category="NaivePhysics")
        static UMaterialInterface* GetMaterialFromName(const FString& Name);

        UFUNCTION(BlueprintCallable, Category="NaivePhysics")
        static UStaticMesh* GetStaticMeshFromName(const FString& Name);
};

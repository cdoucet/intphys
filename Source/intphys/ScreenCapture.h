// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"
#include "ScreenCapture.generated.h"


/**
 * Store depth and mask values for a pixel captured by the
 * CaptureDepthAndMask() function
 */
USTRUCT(BlueprintType)
struct FDepthAndMask
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    float Depth;

    UPROPERTY(BlueprintReadOnly)
    FString Mask;

    FDepthAndMask(){ Depth = 0.0; Mask = FString(); }

    FDepthAndMask(float depth, FString mask){ Depth = depth; Mask = mask; }
};


/**
 * Capture depth, masks and screenshot images of the current scene
 */
UCLASS()
class INTPHYS_API UScreenCapture : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static TArray<FColor> CaptureScene();

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static TArray<FDepthAndMask> CaptureDepthAndMask(
        AActor* OriginActor,
        const FVector2D& ScreenResolution,
        const TArray<AActor*>& IgnoredActors,
        bool verbose = false);
};

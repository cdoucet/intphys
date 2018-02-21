// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ScreenshotManager.h"
#include "Screenshot.generated.h"


/**
 * Exposes function to Python for taking and saving screenshots.
 *
 * This class expose static methods only and wraps a ScreenshotManager
 * instance. The methods delegates operations to that instance.
 */
UCLASS()
class INTPHYS_API UScreenshot : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

private:
    static TSharedPtr<FScreenshotManager> ScreenshotManager;

public:
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Initialize(
        int Width, int Height, int NImages,
        AActor* OriginActor,
        bool Verbose = false);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Capture();

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void Reset();

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void SetOriginActor(AActor* Actor);

};

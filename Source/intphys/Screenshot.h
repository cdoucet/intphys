// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
// #include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"
#include "Screenshot.generated.h"



class FScreenshotManager
{
public:
    typedef TArray<FColor> FImageScene;
    typedef TArray<float> FImageDepth;
    typedef TArray<uint8> FImageMasks;

private:
    FIntVector m_Size;
    bool m_Verbose;
    uint m_ImageIndex;
    TArray<uint8> m_CompressedBitmap;

    TArray<FImageScene> m_Scene;
    TArray<FImageDepth> m_Depth;
    TArray<FImageMasks> m_Masks;
    TMap<FString, uint8> m_MasksMap;

    bool CaptureScene();

    void WritePng(
        TArray<FColor>& Bitmap,
        const FString& Filename);

public:
    FScreenshotManager(
        const FIntVector& Size,
        AActor* OriginActor,
        const TArray<AActor*>& IgnoredActors,
        bool Verbose = false);

    ~FScreenshotManager();

    bool Capture();

    bool Save(const FString& OutputDir);
};


/**
 *
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
        const FIntVector& Size,
        AActor* OriginActor,
        const TArray<AActor*>& IgnoredActors,
        bool Verbose = false);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Capture();

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Save(const FString& OutputDirectory);
};

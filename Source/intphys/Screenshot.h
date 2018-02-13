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
    FString m_OutputDirectory;
    FIntVector m_Size;
    AActor* m_OriginActor;
    bool m_Verbose;
    uint m_ImageIndex;

    // Buffers used in WritePng
    TArray<FColor> m_WriteBuffer;
    TArray<uint8> m_CompressedWriteBuffer;

    TArray<AActor*> m_IgnoredActors;

    TArray<FImageScene> m_Scene;
    TArray<FImageDepth> m_Depth;
    TArray<FImageMasks> m_Masks;
    TMap<FString, uint8> m_MasksMap;

    FString ZeroPadding(uint Index) const;

    bool CaptureScene();
    bool CaptureDepthAndMasks();

    void WritePng(
        TArray<FColor>& Bitmap,
        const FString& Filename);

public:
    FScreenshotManager(
        const FString& OutputDirectory,
        const FIntVector& Size,
        AActor* OriginActor,
        bool Verbose = false);

    ~FScreenshotManager();

    bool Capture();
    bool Save();
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
        const FString& OutputDirectory,
        int Width, int Height, int NImages,
        AActor* OriginActor,
        bool Verbose = false);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Capture();

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Save();
};

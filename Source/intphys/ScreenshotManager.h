// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"


class FScreenshotManager
{
public:
    FScreenshotManager(const FIntVector& Size, AActor* OriginActor, bool Verbose = false);

    ~FScreenshotManager();

    void SetOriginActor(AActor* Actor);

    void SetIgnoredActors(const TArray<AActor*>& IgnoredActors);

    bool Capture();

    bool Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap);

    void Reset();

private:
    // Types of the captured images (they are all saved after a
    // conversion to TArray<uint8>)
    typedef TArray<FColor> FImageScene;
    typedef TArray<float> FImageDepth;
    typedef TArray<uint8> FImageMasks;

    // A triplet (width, height, nimages) of captured images
    FIntVector m_Size;

    // The actor giving the point of view for capture
    AActor* m_OriginActor;

    // Output some log messages when true
    bool m_Verbose;

    // Index of the current image (next to be captured)
    uint m_ImageIndex;

    // Some actors we want to ignore when capturing depth and masks
    TArray<AActor*> m_IgnoredActors;

    // Used to tell the capture to ignore the requested actors
    FCollisionQueryParams m_CollisionQueryParams;

    // World and scene view for depth and mask capture
    UWorld* m_World;
    FSceneView* m_SceneView;

    // Buffers used to store the captured images
    TArray<FImageScene> m_Scene;
    TArray<FImageDepth> m_Depth;
    TArray<FImageMasks> m_Masks;

    // Buffers used in WritePng
    TArray<FColor> m_WriteBuffer;
    TArray<uint8> m_CompressedWriteBuffer;

    // Map the actors names to int ids
    TSet<FString> m_ActorsSet;

    // Take a screenshot of the scene and push it in memory
    bool CaptureScene();

    // Take the scene's depth field and object masking, push them to memory
    bool CaptureDepthAndMasks();

    // Save all the scene images to disk
    bool SaveScene(const FString& Directory);

    // Save all the depth images to disk
    bool SaveDepth(const FString& Directory, float& OutMaxDepth);

    // Save all the masks images to disk
    bool SaveMasks(const FString& Directory, TMap<FString, uint8>& OutMasksMap);

    // Write an image as a PNG file in RGBA format. The alpha channel
    // of the image is forced to 255.
    bool WritePng(const TArray<FColor>& Bitmap, const FString& Filename);

    // Prefix the PNG filenames with zeros : 13 -> "0013"
    FString ZeroPadding(uint Index) const;

};

// Fill out your copyright notice in the Description page of Project Settings.

#include "ScreenshotManager.h"


TSharedPtr<FScreenshot> UScreenshotManager::Screenshot = nullptr;


bool UScreenshotManager::Initialize(
    int Width, int Height, int NImages,
    AActor* OriginActor,
    bool Verbose)
{
    FIntVector Size(Width, Height, NImages);
    Screenshot = TSharedPtr<FScreenshot>(new FScreenshot(Size, OriginActor, Verbose));

    return true;
}


bool UScreenshotManager::Capture(const TArray<AActor*>& IgnoredActors)
{
    return Screenshot->Capture(IgnoredActors);
}

void UScreenshotManager::CaptureMasks(const TArray<AActor*>& IgnoredActors)
{
	Screenshot->CaptureMasks(IgnoredActors);
}

bool UScreenshotManager::Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap)
{
    return Screenshot->Save(Directory, OutMaxDepth, OutActorsMap);
}


void UScreenshotManager::Reset()
{
    Screenshot->Reset();
}


void UScreenshotManager::SetOriginActor(AActor* Actor)
{
    Screenshot->SetOriginActor(Actor);
}


bool UScreenshotManager::IsActorInFrame(AActor* Actor, int FrameIndex)
{
    return Screenshot->IsActorInFrame(Actor, static_cast<uint>(FrameIndex));
}


bool UScreenshotManager::IsActorInLastFrame(AActor* Actor, const TArray<AActor*>& IgnoredActors)
{
    return Screenshot->IsActorInLastFrame(Actor, IgnoredActors);
}

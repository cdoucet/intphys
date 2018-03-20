// Fill out your copyright notice in the Description page of Project Settings.

#include "Screenshot.h"


TSharedPtr<FScreenshotManager> UScreenshot::ScreenshotManager = nullptr;


bool UScreenshot::Initialize(
    int Width, int Height, int NImages,
    AActor* OriginActor,
    bool Verbose)
{
    FIntVector Size(Width, Height, NImages);

    UScreenshot::ScreenshotManager = TSharedPtr<FScreenshotManager>(
        new FScreenshotManager(Size, OriginActor, Verbose));

    return true;
}


bool UScreenshot::Capture()
{
    return UScreenshot::ScreenshotManager->Capture();
}


bool UScreenshot::Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap)
{
    return UScreenshot::ScreenshotManager->Save(
        Directory, OutMaxDepth, OutActorsMap);
}


void UScreenshot::Reset()
{
    UScreenshot::ScreenshotManager->Reset();
}


void UScreenshot::SetOriginActor(AActor* Actor)
{
    UScreenshot::ScreenshotManager->SetOriginActor(Actor);
}


void UScreenshot::SetIgnoredActors(const TArray<AActor*>& Actors)
{
    UScreenshot::ScreenshotManager->SetIgnoredActors(Actors);
}


bool UScreenshot::IsActorInFrame(AActor* Actor, int FrameIndex)
{
    return UScreenshot::ScreenshotManager->IsActorInFrame(
        Actor, static_cast<uint>(FrameIndex));
}


bool UScreenshot::IsActorInLastFrame(AActor* Actor)
{
    return UScreenshot::ScreenshotManager->IsActorInLastFrame(Actor);
}

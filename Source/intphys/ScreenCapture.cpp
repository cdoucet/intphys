// Fill out your copyright notice in the Description page of Project Settings.


#include "ScreenCapture.h"


// Looks up the player's SceneView object modeled after
// APlayerController::GetHitResultAtScreenPosition. From UETorch.
static FSceneView* GetSceneView(APlayerController* PlayerController, UWorld* World)
{
    if(GEngine == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("GEngine null"));
        return NULL;
    }

    if(GEngine->GameViewport == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("GameViewport null"));
        return NULL;
    }

    if(GEngine->GameViewport->Viewport == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Viewport null"));
        return NULL;
    }
    auto Viewport = GEngine->GameViewport->Viewport;

    // Create a view family for the game viewport
    FSceneViewFamilyContext ViewFamily(
        FSceneViewFamily::ConstructionValues(
            Viewport, World->Scene, GEngine->GameViewport->EngineShowFlags)
        .SetRealtimeUpdate(true));

    // Calculate a view where the origin is to update the streaming
    // from the players start location
    FVector ViewLocation;
    FRotator ViewRotation;
    ULocalPlayer* LocalPlayer = Cast<ULocalPlayer>(PlayerController->Player);
    if (LocalPlayer == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Local Player null"));
        return NULL;
    }

    FSceneView* SceneView = LocalPlayer->CalcSceneView(
        &ViewFamily,
        /*out*/ ViewLocation,
        /*out*/ ViewRotation,
        Viewport);

    return SceneView;
}


void TestWriteImage(TArray<FColor>& Bitmap, const FIntVector& Size)
{
    // Force no transparency
    for (FColor& Pixel : Bitmap)
    {
        Pixel.A = 255;
    }

    // Write color image
    TArray<uint8> CompressedBitmap;
    FString ScreenShotName = TEXT("out_color.png");
    FImageUtils::CompressImageArray(Size.X, Size.Y, Bitmap, CompressedBitmap);
    FFileHelper::SaveArrayToFile(CompressedBitmap, *ScreenShotName);

    // Write grayscale image
    ScreenShotName = TEXT("out_ndg.png");
    for (FColor& Pixel : Bitmap)
    {
        uint8 Mean = (Pixel.R + Pixel.G + Pixel.B) / 3;
        Pixel.R = Mean;
        Pixel.G = Mean;
        Pixel.B = Mean;
    }
    FImageUtils::CompressImageArray(Size.X, Size.Y, Bitmap, CompressedBitmap);
    FFileHelper::SaveArrayToFile(CompressedBitmap, *ScreenShotName);
}


TArray<FColor> UScreenCapture::CaptureScene()
{
    TSharedPtr<SWindow> WindowPtr = GEngine->GameViewport->GetWindow();
    if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
    {
        FIntVector OutSize;
        TArray<FColor> Bitmap;
        FSlateApplication::Get().TakeScreenshot(WindowPtr.ToSharedRef(), Bitmap, OutSize);

        TestWriteImage(Bitmap, OutSize);

        return Bitmap;
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("ScreenCapture::CaptureScene failed"));
        return TArray<FColor>();
    }
}


TArray<FDepthAndMask> UScreenCapture::CaptureDepthAndMask(
    AActor* OriginActor,
    const FVector2D& ScreenResolution,
    const TArray<AActor*>& IgnoredActors,
    bool verbose)
{
    UWorld* World = OriginActor->GetWorld();
    FSceneView* SceneView = GetSceneView(
        UGameplayStatics::GetPlayerController(OriginActor, 0), World);

    if (World == NULL || SceneView == NULL)
    {
        UE_LOG(LogTemp, Warning, TEXT("Origin, SceneView or World are null"));
        return TArray<FDepthAndMask>();
    }

    // get the origin location and rotation for distance computation
    FVector OriginLoc = OriginActor->GetActorLocation();
    FVector OriginRot = FRotationMatrix(OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
    OriginRot.Normalize();

    // ignore the requested objects from the raycasting
    FCollisionQueryParams CollisionQueryParams("ClickableTrace", false);
    for (auto& i : IgnoredActors)
        CollisionQueryParams.AddIgnoredActor(i);

    // the returned image
    TArray<FDepthAndMask> Image;

    // for each pixel of the view, cast a ray in the scene and get the
    // resulting hit actor and hit distance
    FHitResult HitResult;
    for (int y = 0; y < ScreenResolution.Y; ++y)
    {
        for (int x = 0; x < ScreenResolution.X; ++x)
	{
            FVector RayOrigin, RayDirection;
            SceneView->DeprojectFVector2D(FVector2D(x, y), RayOrigin, RayDirection);

            bool bHit = World->LineTraceSingleByChannel(
                HitResult, RayOrigin, RayOrigin + RayDirection * 1000000.f,
                ECollisionChannel::ECC_Visibility, CollisionQueryParams);

            if(bHit)
            {
                float HitDistance = FVector::DotProduct(HitResult.Location - OriginLoc, OriginRot);
                Image.Add(FDepthAndMask(HitDistance, HitResult.GetActor()->GetName()));
            }
            else
            {
                Image.Add(FDepthAndMask());
            }

            // log a debug message with ray coordinates of the first
            // pixel only
            if(verbose)
            {
                UE_LOG(
                    LogTemp, Log,
                    TEXT("Capture: camera origin = (%f, %f, %f), rotation = (%f, %f, %f)"),
                    OriginLoc.X, OriginLoc.Y, OriginLoc.Z,
                    OriginRot.X, OriginRot.Y, OriginRot.Z);

                FVector ViewLoc = SceneView->ViewLocation;
                FRotator ViewRot = SceneView->ViewRotation;
                UE_LOG(
                    LogTemp, Log,
                    TEXT("Capture: view origin = (%f, %f, %f), rotation = (%f, %f, %f)"),
                    ViewLoc.X, ViewLoc.Y, ViewLoc.Z,
                    ViewRot.Pitch, ViewRot.Roll, ViewRot.Yaw);

                UE_LOG(
                    LogTemp, Log,
                    TEXT("Capture: ray origin = (%f, %f, %f), direction = (%f, %f, %f)"),
                    RayOrigin.X, RayOrigin.Y, RayOrigin.Z,
                    RayDirection.X, RayDirection.Y, RayDirection.Z);

                verbose = false;
            }
        }
    }

    return Image;
}

// Fill out your copyright notice in the Description page of Project Settings.

#include "Screenshot.h"
#include "ImageUtils.h"
#include "Runtime/Core/Public/HAL/PlatformFilemanager.h"
#include "Runtime/Core/Public/GenericPlatform/GenericPlatformMath.h"
#include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"


static bool VerifyOrCreateDirectory(const FString& Directory)
{
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

    if (!PlatformFile.DirectoryExists(*Directory))
    {
        PlatformFile.CreateDirectory(*Directory);

        if (!PlatformFile.DirectoryExists(*Directory))
        {
            return false;
        }
    }

    return true;
}


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


TSharedPtr<FScreenshotManager> UScreenshot::ScreenshotManager = nullptr;


bool UScreenshot::Initialize(
    const FString& OutputDirectory,
    int Width, int Height, int NImages,
    AActor* OriginActor,
    bool Verbose)
{
    FIntVector Size(Width, Height, NImages);

    UScreenshot::ScreenshotManager = TSharedPtr<FScreenshotManager>(
        new FScreenshotManager(OutputDirectory, Size, OriginActor, Verbose));

    return true;
}


bool UScreenshot::Capture()
{
    return UScreenshot::ScreenshotManager->Capture();
}


bool UScreenshot::Save()
{
    return UScreenshot::ScreenshotManager->Save();
}


FScreenshotManager::FScreenshotManager(
    const FString& OutputDirectory,
    const FIntVector& Size,
    AActor* OriginActor,
    bool Verbose):
    m_OutputDirectory(OutputDirectory),
    m_Size(Size),
    m_OriginActor(OriginActor),
    m_Verbose(Verbose),
    m_ImageIndex(0)
{
    // allocate memory for storing images
    m_Scene.SetNum(Size.Z);
    for (auto& Picture : m_Scene)
        Picture.SetNum(Size.X * Size.Y);

    m_Depth.SetNum(Size.Z);
    for (auto& Picture : m_Depth)
        Picture.SetNum(Size.X * Size.Y);

    m_Masks.SetNum(Size.Z);
    for (auto& Picture : m_Masks)
        Picture.SetNum(Size.X * Size.Y);

    m_WriteBuffer.SetNum(Size.X * Size.Y);
    m_CompressedWriteBuffer.SetNum(Size.X * Size.Y);
}


FScreenshotManager::~FScreenshotManager()
{}


bool FScreenshotManager::Capture()
{
    // if (m_Verbose)
    // {
    //     UE_LOG(LogTemp, Log, TEXT("Capturing (tick %d)"), m_ImageIndex+1);
    // }

    if (m_ImageIndex >= m_Size.Z)
    {
        UE_LOG(LogTemp, Error, TEXT("Screen capture failed: too mush images captured"));
        return false;
    }

    bool SceneDone = FScreenshotManager::CaptureScene();
    bool DepthAndMasksDone = FScreenshotManager::CaptureDepthAndMasks();

    // Update the counter to push the next image
    m_ImageIndex++;

    return SceneDone and DepthAndMasksDone;
}


bool FScreenshotManager::Save()
{
    // Create the subdirectories
    for (const auto& Name : {TEXT("scene"), TEXT("masks"), TEXT("depth")})
    {
        FString Directory = FPaths::Combine(m_OutputDirectory, FString(Name));
        VerifyOrCreateDirectory(Directory);
    }

    // Extract the global max depth
    TArray<float> MaxDepthArray;
    for (const auto& Image : m_Depth)
    {
        MaxDepthArray.Add(FMath::Max(Image));
    }
    float MaxDepth = FMath::Max(MaxDepthArray);

    if (m_Verbose)
    {
        UE_LOG(LogTemp, Log, TEXT("Max depth is %f"), MaxDepth);

        FString Map;
        for (const auto& Elem : m_MasksMap)
        {
            Map +=
        }
        UE_LOG(LogTemp, Log, TEXT("Masks are %s"))
    }

    for (uint i = 0; i < m_Size.Z; ++i)
    {
        FString FileIndex = FScreenshotManager::ZeroPadding(i+1);

        // save the scene
        FString Filename = FPaths::Combine(
            m_OutputDirectory, TEXT("scene"),
            FString::Printf(TEXT("scene_%s.png"), *FileIndex));
        FScreenshotManager::WritePng(m_Scene[i], Filename);

        // save the normalized depth
        Filename = FPaths::Combine(
            m_OutputDirectory, TEXT("depth"),
            FString::Printf(TEXT("depth_%s.png"), *FileIndex));
        for(uint j = 0; j < m_Depth[i].Num(); ++j)
        {
            uint8 Pixel = (uint8)(m_Depth[i][j] * 255.0 / MaxDepth);
            m_WriteBuffer[j] = FColor(Pixel, Pixel, Pixel, 255);
        }
        FScreenshotManager::WritePng(m_WriteBuffer, Filename);

        // save the normalized masks
        Filename = FPaths::Combine(
            m_OutputDirectory, TEXT("masks"),
            FString::Printf(TEXT("masks_%s.png"), *FileIndex));

    }

    return true;
}


bool FScreenshotManager::CaptureScene()
{
    TSharedPtr<SWindow> WindowPtr = GEngine->GameViewport->GetWindow();
    if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
    {
        FIntVector OutSize;
        TArray<FColor> Bitmap;
        bool CaptureDone = FSlateApplication::Get().TakeScreenshot(
            WindowPtr.ToSharedRef(), m_Scene[m_ImageIndex], OutSize);

        return CaptureDone;
    }
    else
    {
        return false;
    }
}


bool FScreenshotManager::CaptureDepthAndMasks()
{
    UWorld* World = m_OriginActor->GetWorld();
    FSceneView* SceneView = GetSceneView(
        UGameplayStatics::GetPlayerController(m_OriginActor, 0), World);

    if (World == NULL || SceneView == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Origin, SceneView or World are null"));
        return false;
    }

    // get the origin location and rotation for distance computation
    FVector OriginLoc = m_OriginActor->GetActorLocation();
    FVector OriginRot = FRotationMatrix(m_OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
    OriginRot.Normalize();

    // ignore the requested objects from the raycasting
    FCollisionQueryParams CollisionQueryParams("ClickableTrace", false);
    for (auto& i : m_IgnoredActors)
        CollisionQueryParams.AddIgnoredActor(i);

    // for each pixel of the view, cast a ray in the scene and get the
    // resulting hit actor and hit distance
    FHitResult HitResult;
    for (int y = 0; y < m_Size.Y; ++y)
    {
        for (int x = 0; x < m_Size.X; ++x)
	{
            FVector RayOrigin, RayDirection;
            SceneView->DeprojectFVector2D(FVector2D(x, y), RayOrigin, RayDirection);

            bool bHit = World->LineTraceSingleByChannel(
                HitResult, RayOrigin, RayOrigin + RayDirection * 1000000.f,
                ECollisionChannel::ECC_Visibility, CollisionQueryParams);

            if(bHit)
            {
                uint PixelIndex = y * m_Size.X + x;

                // compute depth
                float HitDistance = FVector::DotProduct(HitResult.Location - OriginLoc, OriginRot);
                m_Depth[m_ImageIndex][PixelIndex] = HitDistance;

                // compute mask
                FString HitActorName = HitResult.GetActor()->GetName();
                uint8& HitActorId = m_MasksMap.FindOrAdd(HitActorName);
                if (HitActorId == 0)  // the actor is not yet in the map, add it
                {
                    HitActorId = m_MasksMap.Num() + 1;
                }
                m_Masks[m_ImageIndex][PixelIndex] = HitActorId;
            }

            // // log a debug message with ray coordinates
            // if(m_Verbose)
            // {
            //     UE_LOG(
            //         LogTemp, Log,
            //         TEXT("Capture: camera origin = (%f, %f, %f), rotation = (%f, %f, %f)"),
            //         OriginLoc.X, OriginLoc.Y, OriginLoc.Z,
            //         OriginRot.X, OriginRot.Y, OriginRot.Z);

            //     FVector ViewLoc = SceneView->ViewLocation;
            //     FRotator ViewRot = SceneView->ViewRotation;
            //     UE_LOG(
            //         LogTemp, Log,
            //         TEXT("Capture: view origin = (%f, %f, %f), rotation = (%f, %f, %f)"),
            //         ViewLoc.X, ViewLoc.Y, ViewLoc.Z,
            //         ViewRot.Pitch, ViewRot.Roll, ViewRot.Yaw);

            //     UE_LOG(
            //         LogTemp, Log,
            //         TEXT("Capture: ray origin = (%f, %f, %f), direction = (%f, %f, %f)"),
            //         RayOrigin.X, RayOrigin.Y, RayOrigin.Z,
            //         RayDirection.X, RayDirection.Y, RayDirection.Z);
            // }
        }
    }

    return true;
}


void FScreenshotManager::WritePng(TArray<FColor>& Bitmap, const FString& Filename)
{
    // Force no transparency
    for (FColor& Pixel : Bitmap)
    {
        Pixel.A = 255;
    }

    // Write RGBA PNG image
    FImageUtils::CompressImageArray(m_Size.X, m_Size.Y, Bitmap, m_CompressedWriteBuffer);
    FFileHelper::SaveArrayToFile(m_CompressedWriteBuffer, *Filename);
}


FString FScreenshotManager::ZeroPadding(uint Index) const
{
    FString SIndex = FString::FromInt(Index);
    FString SMax = FString::FromInt(m_Size.Z);

    return FString::ChrN(SMax.Len() - SIndex.Len(), '0') + SIndex;
}

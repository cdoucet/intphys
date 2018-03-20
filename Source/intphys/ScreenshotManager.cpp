#include "ScreenshotManager.h"

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


FScreenshotManager::FScreenshotManager(const FIntVector& Size, AActor* OriginActor, bool Verbose):
    m_Size(Size), m_OriginActor(OriginActor), m_Verbose(Verbose),
    m_ImageIndex(0), m_CollisionQueryParams("ClickableTrace", false)
{
    // allocate memory for storing images
    m_Scene.SetNum(Size.Z);
    for (auto& Image : m_Scene)
        Image.SetNum(Size.X * Size.Y);

    m_Depth.SetNum(Size.Z);
    for (auto& Image : m_Depth)
        Image.SetNum(Size.X * Size.Y);

    m_Masks.SetNum(Size.Z);
    for (auto& Image : m_Masks)
        Image.SetNum(Size.X * Size.Y);

    m_WriteBuffer.SetNum(Size.X * Size.Y);
    m_CompressedWriteBuffer.SetNum(Size.X * Size.Y);
}


FScreenshotManager::~FScreenshotManager()
{}


void FScreenshotManager::SetIgnoredActors(const TArray<AActor*>& Actors)
{
    // clear any registered actor
    m_CollisionQueryParams.ClearIgnoredComponents();

    // ignore the requested objects from the raycasting
    for (auto& i : m_IgnoredActors)
        m_CollisionQueryParams.AddIgnoredActor(i);
}


void FScreenshotManager::SetOriginActor(AActor* Actor)
{
    m_OriginActor = Actor;
}


bool FScreenshotManager::Capture()
{
    // if (m_Verbose)
    // {
    //     UE_LOG(LogTemp, Log, TEXT("Capturing (tick %d)"), m_ImageIndex+1);
    // }

    if (m_ImageIndex >= m_Size.Z)
    {
        UE_LOG(LogTemp, Error, TEXT("Screen capture failed: too much images captured"));
        return false;
    }

    bool bDone1 = FScreenshotManager::CaptureScene();
    bool bDone2 = FScreenshotManager::CaptureDepthAndMasks();

    // Update the counter
    m_ImageIndex++;

    return bDone1 and bDone2;
}


bool FScreenshotManager::Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap)
{
    // Create the subdirectories where to write the PNGs
    for (const auto& Name : {TEXT("scene"), TEXT("masks"), TEXT("depth")})
    {
        FString SubDirectory = FPaths::Combine(Directory, FString(Name));
        VerifyOrCreateDirectory(SubDirectory);
    }

    // Save the images
    bool bScene = SaveScene(FPaths::Combine(Directory, FString("scene")));
    bool bMasks = SaveMasks(FPaths::Combine(Directory, FString("masks")), OutActorsMap);
    bool bDepth = SaveDepth(FPaths::Combine(Directory, FString("depth")), OutMaxDepth);

    bool bDone = bScene and bMasks and bDepth;
    if (not bDone)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to save captured images"));
    }

    return bDone;
}


void FScreenshotManager::Reset()
{
    m_ImageIndex = 0;
    m_ActorsSet.Empty();
    m_ActorsMap.Empty();
}


bool FScreenshotManager::IsActorInFrame(const AActor* Actor, const uint FrameIndex)
{
    if (FrameIndex >= m_ImageIndex)
    {
        return false;
    }

    uint8 ActorId = m_ActorsMap[Actor->GetName()];
    return m_Masks[FrameIndex].Contains(ActorId);
}


bool FScreenshotManager::IsActorInLastFrame(const AActor* Actor)
{
    return IsActorInFrame(Actor, m_ImageIndex-1);
}


bool FScreenshotManager::CaptureScene()
{
    TSharedPtr<SWindow> WindowPtr = GEngine->GameViewport->GetWindow();
    if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
    {
        FIntVector OutSize;
        bool bDone = FSlateApplication::Get().TakeScreenshot(
            WindowPtr.ToSharedRef(), m_Scene[m_ImageIndex], OutSize);

        // Force no transparency
        if (bDone)
        {
            for (FColor& Pixel : m_Scene[m_ImageIndex])
            {
                Pixel.A = 255;
            }
        }

        return bDone;
    }
    else
    {
        return false;
    }
}


bool FScreenshotManager::CaptureDepthAndMasks()
{
    // Intitialize world and scene view
    m_World = m_OriginActor->GetWorld();
    m_SceneView = GetSceneView(UGameplayStatics::GetPlayerController(m_OriginActor, 0), m_World);

    if (m_World == NULL || m_SceneView == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("ScreenshotManager: SceneView or World are null"));
    }

    // get the origin location and rotation for distance computation
    FVector OriginLoc = m_OriginActor->GetActorLocation();
    FVector OriginRot = FRotationMatrix(m_OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
    OriginRot.Normalize();

    // for each pixel of the view, cast a ray in the scene and get the
    // resulting hit actor and hit distance
    FHitResult HitResult;
    for (int y = 0; y < m_Size.Y; ++y)
    {
        for (int x = 0; x < m_Size.X; ++x)
	{
            FVector RayOrigin, RayDirection;
            m_SceneView->DeprojectFVector2D(FVector2D(x, y), RayOrigin, RayDirection);

            bool bHit = m_World->LineTraceSingleByChannel(
                HitResult, RayOrigin, RayOrigin + RayDirection * 1000000.f,
                ECollisionChannel::ECC_Visibility, m_CollisionQueryParams);

            if(bHit)
            {
                uint PixelIndex = y * m_Size.X + x;

                // compute depth
                float HitDistance = FVector::DotProduct(HitResult.Location - OriginLoc, OriginRot);
                m_Depth[m_ImageIndex][PixelIndex] = HitDistance;

                // compute mask
                FString ActorName = HitResult.GetActor()->GetName();
                int8 ActorIndex = static_cast<uint8>(m_ActorsSet.Add(ActorName).AsInteger() + 1);
                m_ActorsMap.Add(ActorName, ActorIndex);
                m_Masks[m_ImageIndex][PixelIndex] = ActorIndex;
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


bool FScreenshotManager::SaveScene(const FString& Directory)
{
    for (uint i = 0; i < m_Size.Z; ++i)
    {
        // build the filename
        FString FileIndex = FScreenshotManager::ZeroPadding(i+1);
        FString Filename = FPaths::Combine(
            Directory, FString::Printf(TEXT("scene_%s.png"), *FileIndex));

        // write the image
        bool bDone = FScreenshotManager::WritePng(m_Scene[i], Filename);
        if (not bDone)
        {
            return false;
        }
    }

    return true;
}


bool FScreenshotManager::SaveDepth(const FString& Directory, float& OutMaxDepth)
{
    // Extract the global max depth
    TArray<float> MaxDepthArray;
    for (const auto& Image : m_Depth)
    {
        MaxDepthArray.Add(FMath::Max(Image));
    }
    OutMaxDepth = FMath::Max(MaxDepthArray);

    if (m_Verbose)
    {
        UE_LOG(LogTemp, Log, TEXT("Max depth is %f"), OutMaxDepth);
    }

    for (uint i = 0; i < m_Size.Z; ++i)
    {
        // build the filename
        FString FileIndex = FScreenshotManager::ZeroPadding(i+1);
        FString Filename = FPaths::Combine(
            Directory, FString::Printf(TEXT("depth_%s.png"), *FileIndex));

        // normalize the depth in [0, 1] and cast to uint8
        FImageDepth& Image = m_Depth[i];
        for(uint j = 0; j < Image.Num(); ++j)
        {
            uint8 Pixel = static_cast<uint8>(Image[j] * 255.0 / OutMaxDepth);
            m_WriteBuffer[j] = FColor(Pixel, Pixel, Pixel, 255);
        }

        // write the image
        bool bDone = FScreenshotManager::WritePng(m_WriteBuffer, Filename);
        if (not bDone)
        {
            return false;
        }
    }

    return true;
}


bool FScreenshotManager::SaveMasks(const FString& Directory, TMap<FString, uint8>& OutActorsMap)
{
    // build the actors name -> gray level mapping
    OutActorsMap.Empty(m_ActorsSet.Num() + 1);
    OutActorsMap.Add(FString(TEXT("Sky")), 0);
    for (const FString& ActorName : m_ActorsSet)
    {
        auto Index = m_ActorsSet.Add(ActorName).AsInteger() + 1;
        uint8 Pixel = static_cast<uint8>(Index * 255.0 / m_ActorsSet.Num());
        OutActorsMap.Add(ActorName, Pixel);
    }

    if (m_Verbose)
    {
        FString MasksStr;
        for (auto& Elem : OutActorsMap)
        {
            MasksStr += FString::Printf(TEXT("(%s, %d) "), *Elem.Key, Elem.Value);
        }
        UE_LOG(LogTemp, Log, TEXT("Actors masks are %s"), *MasksStr);
    }

    for (uint i = 0; i < m_Size.Z; ++i)
    {
        // build the filename
        FString FileIndex = FScreenshotManager::ZeroPadding(i+1);
        FString Filename = FPaths::Combine(
            Directory, FString::Printf(TEXT("masks_%s.png"), *FileIndex));

        // normalize masks from [0, nactors-1] to [0, 255]
        FImageMasks& Image = m_Masks[i];
        for (uint j = 0; j < Image.Num(); ++j)
        {
            uint8 Pixel = static_cast<uint8>(Image[j] * 255.0 / m_ActorsSet.Num());
            m_WriteBuffer[j] = FColor(Pixel, Pixel, Pixel, 255);
        }

        // write the image
        bool bDone = FScreenshotManager::WritePng(m_WriteBuffer, Filename);
        if (not bDone)
        {
            return false;
        }
    }

    return true;

    // TMap<FString, FColor> MasksNameMap;
    // TMap<uint8, FColor> MasksIndexMap;
    // m_ActorsSet.Sort([](const FString& A, const FString& B) {return A < B;});
    // for (const FString& Actor : m_ActorsSet)
    // {
    //     uint8 Index = static_cast<uint8>(m_ActorsSet.Add(Actor).AsInteger());
    //     uint8 GrayIndex = Index * 255 / (float)m_ActorsSet.Num();
    //     FColor GrayColor(GrayIndex, GrayIndex, GrayIndex, 255);
    //     MasksNameMap[Actor] = GrayColor;
    //     MasksIndexMap[Index] = GrayColor;
    // }
}


bool FScreenshotManager::WritePng(const TArray<FColor>& Bitmap, const FString& Filename)
{
    FImageUtils::CompressImageArray(m_Size.X, m_Size.Y, Bitmap, m_CompressedWriteBuffer);
    bool bDone = FFileHelper::SaveArrayToFile(m_CompressedWriteBuffer, *Filename);

    if (not bDone)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to write %s"), *Filename);
    }

    return bDone;
}


FString FScreenshotManager::ZeroPadding(uint Index) const
{
    FString SIndex = FString::FromInt(Index);
    FString SMax = FString::FromInt(m_Size.Z);

    return FString::ChrN(SMax.Len() - SIndex.Len(), '0') + SIndex;
}

// Fill out your copyright notice in the Description page of Project Settings.


#include "Screenshot.h"
#include "ImageUtils.h"
#include "Runtime/Core/Public/HAL/PlatformFilemanager.h"


//If this function cannot find or create the directory, returns false.
static bool VerifyOrCreateDirectory(const FString& Directory)
{
    // Every function call, unless the function is inline, adds a small
    // overhead which we can avoid by creating a local variable like so.
    // But beware of making every function inline!
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

    // Directory Exists?
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


bool UScreenshot::Initialize(const FIntVector& Size, AActor* OriginActor,
                             const TArray<AActor*>& IgnoredActors, bool Verbose)
{
    TSharedPtr<FScreenshotManager> Manager(
        new FScreenshotManager(Size, OriginActor, IgnoredActors, Verbose));
    UScreenshot::ScreenshotManager = TSharedPtr<FScreenshotManager>(Manager);

    return true;
}


bool UScreenshot::Capture()
{
    return UScreenshot::ScreenshotManager->Capture();
}


bool UScreenshot::Save(const FString& OutputDirectory)
{
    return UScreenshot::ScreenshotManager->Save(OutputDirectory);
}


FScreenshotManager::FScreenshotManager(const FIntVector& Size, AActor* OriginActor,
                                       const TArray<AActor*>& IgnoredActors, bool Verbose):
    m_Size(Size), m_Verbose(Verbose), m_ImageIndex(0)
{
    // allocate memory for storing images
    m_Scene.SetNum(Size.Z);
    for (auto& Picture : m_Scene)
        Picture.SetNum(Size.X * Size.Y);
}


FScreenshotManager::~FScreenshotManager()
{}


bool FScreenshotManager::Capture()
{
    if (m_Verbose)
    {
        UE_LOG(LogTemp, Log, TEXT("Capturing (tick %d)"), m_ImageIndex+1);
    }

    if (m_ImageIndex >= m_Size.Z)
    {
        UE_LOG(LogTemp, Error, TEXT("Screen capture failed: too mush images captured"));
        return false;
    }

    bool SceneDone = this->CaptureScene();

    // Update the counter to push the next image
    m_ImageIndex++;

    return SceneDone;
}


bool FScreenshotManager::Save(const FString& OutputDirectory)
{
    FString Directory = FPaths::Combine(OutputDirectory, FString(TEXT("scene")));
    VerifyOrCreateDirectory(Directory);
    for (uint i = 0; i < m_Size.Z; ++i)
    {
        FString Filename = FString::Printf(TEXT("scene_%d.png"), i+1);
        FString AbsFilename = FPaths::Combine(Directory, Filename);

        this->WritePng(m_Scene[i], Filename);
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
        bool SceneDone = FSlateApplication::Get().TakeScreenshot(
            WindowPtr.ToSharedRef(), m_Scene[m_ImageIndex], OutSize);

        return SceneDone;
    }
    else
    {
        return false;
    }
}


void FScreenshotManager::WritePng(TArray<FColor>& Bitmap, const FString& Filename)
{
    // Force no transparency
    for (FColor& Pixel : Bitmap)
    {
        Pixel.A = 255;
    }

    if (m_Verbose)
        UE_LOG(LogTemp, Log, TEXT("Writing %s"), *Filename);

    // Write RGBA image
    FImageUtils::CompressImageArray(m_Size.X, m_Size.Y, Bitmap, m_CompressedBitmap);
    FFileHelper::SaveArrayToFile(m_CompressedBitmap, *Filename);
}

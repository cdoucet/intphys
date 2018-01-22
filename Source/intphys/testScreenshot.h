// Mathieu Bernard, Mario Ynocente Castro, Erwan Simon

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"
#include "testScreenshot.generated.h"

USTRUCT(BlueprintType)
struct FIntSize
{
  GENERATED_BODY()

  UPROPERTY(BlueprintReadOnly)
  int32 X;

  UPROPERTY(BlueprintReadOnly)
  int32 Y;

  FIntSize()
  {
    X = 0;
    Y = 0;
  }

  FIntSize(int32 x, int32 y)
  {
    X = x;
    Y = y;
  }
};

UCLASS()
class INTPHYS_API UtestScreenshot : public UBlueprintFunctionLibrary
{
  GENERATED_BODY()

private:

public:

  // UFUNCTION(BlueprintCallable, Category="IntPhys")
  // static bool CaptureDepthAndMasks(
  //     const FIntSize& size, int stride, AActor* origin,
  //     const TArray<AActor*>& objects,
  //     const TArray<AActor*>& ignoredObjects,
  //     TArray<FColor>& depth_data, TArray<FColor>& mask_data);

  UFUNCTION(BlueprintCallable, Category="InyPhys")
  static TArray<float> CaptureDepth(
      const FIntSize& size,
      int stride,
      AActor* origin,
      const TArray<AActor*>& objects,
      const TArray<AActor*>& ignoredObjects);

  // UFUNCTION(BlueprintCallable, Category="IntPhys")
  // static TArray<int> CaptureMask(
  //     const FIntSize& size, int stride, AActor* origin,
  //     const TArray<AActor*>& objects,
  //     const TArray<AActor*>& ignoredObjects);

  UFUNCTION(BlueprintCallable, Category="IntPhys")
  static TArray<int> CaptureScreenshot(
      const FIntSize& size);

  UFUNCTION(BlueprintCallable, Category="IntPhys")
  static bool JustARay(UWorld* World, const FVector& From, const FVector& To);

  // UFUNCTION(BlueprintCallable, Category="IntPhys")
  // static bool DoTheWholeStuff(
  //     const FIntSize& size, int stride, AActor* origin,
  //     const TArray<AActor*>& objects,
  //     const TArray<AActor*>& ignoredObjects);

  UFUNCTION(BlueprintCallable, Category="IntPhys")
  static FString BuildFileName(
      int flag);
};

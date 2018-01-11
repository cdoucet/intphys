// Mathieu Bernard, Mario Ynocente Castro, Erwan Simon

#include "testScreenshot.h"
#include <string.h>
#include <memory>
#include <sstream>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>
#include <iostream>
#include <fstream>
#include <ctime>
#include <cmath>
#include "DrawDebugHelpers.h"

static FSceneView* GetSceneView(
    APlayerController* PlayerController,
    UWorld* World)
{
    if (GEngine == NULL || GEngine->GameViewport == NULL || GEngine->GameViewport->Viewport == NULL)
    {
        UE_LOG(LogTemp, Warning, TEXT("Viewport creation problem"));
        return NULL;
    }

    auto Viewport = GEngine->GameViewport->Viewport;
    // Create a view family for the game viewport
    FSceneViewFamilyContext ViewFamily(
        FSceneViewFamily::ConstructionValues(
            Viewport,
            World->Scene,
            GEngine->GameViewport->EngineShowFlags).SetRealtimeUpdate(true));

    // Calculate a view where the player is to update the streaming
    // from the players start location
    FVector ViewLocation;
    FRotator ViewRotation;
    ULocalPlayer* LocalPlayer = Cast<ULocalPlayer>(PlayerController->Player);
    if (LocalPlayer == NULL)
        return NULL;

    FSceneView* SceneView = LocalPlayer->CalcSceneView(
        &ViewFamily,
        /*out*/ ViewLocation,
        /*out*/ ViewRotation, Viewport);
    return SceneView;
}

static void FSceneView__SafeDeprojectFVector2D(
    const FSceneView* SceneView,
    const FVector2D& ScreenPos,
    FVector& WorldOrigin,
    FVector& WorldDirection)
{
    const FMatrix InverseViewMatrix = SceneView->ViewMatrices.GetViewMatrix().Inverse();
    const FMatrix InvProjectionMatrix = SceneView->ViewMatrices.GetInvViewMatrix();

    SceneView->DeprojectScreenToWorld(
        ScreenPos, SceneView->UnscaledViewRect,
        InverseViewMatrix, InvProjectionMatrix,
        WorldOrigin, WorldDirection);
}

TArray<int> UtestScreenshot::CaptureDepth(
    const FIntSize& size, int stride,
    AActor* origin,
    const TArray<AActor*>& objects,
    const TArray<AActor*>& ignoredObjects)
{
  TArray<int>		Result;
  UWorld*		World = NULL;
  FSceneView*		SceneView = NULL;
  FVector		PlayerLoc, PlayerF, WorldOrigin, WorldDirection;
  FHitResult		HitResult;
  FCollisionQueryParams	*CollisionQueryParams = NULL;
  bool			DidItWork = false;

  if (origin == NULL || (World = origin->GetWorld()) == NULL ||
      (SceneView = GetSceneView(UGameplayStatics::GetPlayerController(origin, 0), World)) == NULL)
  {
      UE_LOG(LogTemp, Warning, TEXT("Origin, SceneView or World are null"));
      return Result;
  }
  PlayerLoc = origin->GetActorLocation();
  PlayerF = FRotationMatrix(origin->GetActorRotation()).GetScaledAxis(EAxis::X);
  PlayerF.Normalize();

  if ((CollisionQueryParams = new FCollisionQueryParams("ClickableTrace", false)) == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("CollisionQueryParams is null"));
      return Result;
    }
  for (auto& i : ignoredObjects)
    CollisionQueryParams->AddIgnoredActor(i);

  for (float y = 0; y < size.Y; y += stride)
    {
      for (float x = 0; x < size.X; x += stride)
	{
	  FSceneView__SafeDeprojectFVector2D(
              SceneView, FVector2D(x, y),
              WorldOrigin, WorldDirection);

	  // DrawDebugLine( // draw a line
	  // 		World,
	  // 		WorldOrigin, // from here
	  // 		WorldOrigin + WorldDirection, // to here
	  // 		FColor(255,0,0),
	  // 		true, -1, 0,
	  // 		12.333
	  // 		);

	  if (World->LineTraceSingleByChannel(
                  HitResult, WorldOrigin,
                  WorldOrigin + WorldDirection * 1000000.f,
                  ECollisionChannel::ECC_Visibility,
                  *CollisionQueryParams))
          {
	      const auto &HitLoc = HitResult.Location;

              // distance between camera and actor (irrelevant because
              // not bind to each different pixel)
	      double distance = sqrt(
                  pow(PlayerLoc.X - HitLoc.X, 2) +
                  pow(PlayerLoc.Y - HitLoc.Y, 2) +
                  pow(PlayerLoc.Z - HitLoc.Z, 2));

	      double dotProduct = FVector::DotProduct(HitLoc, PlayerF);

              // UE_LOG(LogTemp, Log, TEXT("dotproduct: %f"), dotProduct);
	      // UE_LOG(LogTemp, Log, TEXT("distance: %f"), distance);
	      for (int i = 0; i != 3; i += 1)
                  // the formula make the dotProduct be between 0 and
                  // 254 (base value being between -1 and 1)
                  Result.Add((FVector::DotProduct(HitLoc - PlayerLoc, PlayerF) + 1) * 127);
	      //Result.Add(dotProduct);
	      DidItWork = true;
          }
	  else
	      for (int i = 0; i != 3; i += 1)
                  Result.Add(0);
	  // UE_LOG(LogTemp, Log, TEXT("\nWorldOrigin:%f/%f/%f\nWorldDirection:%f/%f/%f"),
          //        WorldOrigin.X, WorldOrigin.Y, WorldOrigin.Z,
          //        WorldDirection.X, WorldDirection.Y, WorldDirection.Z);
	}
    }

  //UE_LOG(LogTemp, Log, TEXT("number of pixels : %d"), Result.Num() / 3);

  if (DidItWork == false)
    Result.Empty();

  return (Result);
}


// I'm a little depressed about returning an array by copy... Really
// sorry about that If you know how to do it differently, please do
TArray<int> UtestScreenshot::CaptureScreenshot(const FIntSize& givenSize)
{
  TArray<FColor>	Bitmap;
  FViewport*		Viewport = NULL;
  TSharedPtr<SWindow>	WindowPtr = NULL;
  FIntVector		returnedSize;
  FIntRect		Rect;
  TArray<int>		Result;

  if (GEngine == NULL || GEngine->GameViewport == NULL ||
      (Viewport = GEngine->GameViewport->Viewport) == NULL)
  {
      UE_LOG(LogTemp, Warning, TEXT("Something went NULL in screenshot initialization"));
      return Result;
  }

  if (givenSize.X != Viewport->GetSizeXY().X || givenSize.Y != Viewport->GetSizeXY().Y)
    {
      UE_LOG(LogTemp, Warning, TEXT(
                 "Real viewport size and given size are different.\n"
                 "Viewport size : %d * %d\nSend size : %d * %d"),
	     Viewport->GetSizeXY().X, Viewport->GetSizeXY().Y,
             givenSize.X, givenSize.Y);

      return Result;
    }

  WindowPtr = GEngine->GameViewport->GetWindow();
  if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
    {
      returnedSize = FIntVector(givenSize.X, givenSize.Y, 0);
      FSlateApplication::Get().TakeScreenshot(
          WindowPtr.ToSharedRef(),
          Bitmap, returnedSize);

      //UE_LOG(LogTemp, Log, TEXT("Screenshot size : %d * %d"),
      //	     returnedSize.X, returnedSize.Y);
    }
  else
    {
      UE_LOG(LogTemp, Warning, TEXT("NULL window"));
      return Result;
    }

  for(FColor color : Bitmap) {
    Result.Add(color.R);
    Result.Add(color.G);
    Result.Add(color.B);
  }
  return Result;
}

// the filename format will be, for instance,
// screenshot_%day-%month-%year_%hour:%minute:%second
FString	UtestScreenshot::BuildFileName(int flag)
{
  time_t	rawtime;
  struct tm *	timeinfo;
  char		buffer[25];
  std::string	str;

  time(&rawtime);
  timeinfo = localtime(&rawtime);
  strftime(buffer,sizeof(buffer),"%d-%m-%Y_%I:%M:%S",timeinfo);
  str = buffer;
  switch (flag)
    {
    case 1:
      str = "screenshot_" + str + ".png";
      break;
    case 2:
      str = "depth_" + str + ".png";
      break;
    case 3:
      str = "mask_" + str + ".png";
      break;
    default:
      UE_LOG(LogTemp, Warning, TEXT("The flag send to build the filename is wrong."));
      str = "WrongFlagInFileName.png";
      break;
    }
  return (UTF8_TO_TCHAR(str.c_str()));
}



// TArray<int>	UtestScreenshot::CaptureMask(const FIntSize& size, int stride, AActor* origin,
// 					      const TArray<AActor*>& objects,
// 					      const TArray<AActor*>& ignoredObjects)
// {
//   TArray<int>		Result;
//   UWorld*		World = NULL;
//   FSceneView*		SceneView = NULL;
//   FVector		PlayerLoc, PlayerF, WorldOrigin, WorldDirection, HitLocRel;
//   FHitResult		HitResult;
//   FCollisionQueryParams	*CollisionQueryParams = NULL;
//   bool			DidItWork = false;

//   if (origin == NULL || (World = origin->GetWorld()) == NULL ||
//       (SceneView = GetSceneView(UGameplayStatics::GetPlayerController(origin, 0), World)) == NULL)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("Origin, SceneView or World are null"));
//       return Result;
//     }
//   PlayerLoc = origin->GetActorLocation();
//   PlayerF = FRotationMatrix(origin->GetActorRotation()).GetScaledAxis(EAxis::X);
//   PlayerF.Normalize();
//   if ((CollisionQueryParams = new FCollisionQueryParams("ClickableTrace", false)) == NULL)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("CollisionQueryParams is null"));
//       return Result;
//     }
//   for (auto& i : ignoredObjects)
//     CollisionQueryParams->AddIgnoredActor(i);
//   int j = 1;
//   AActor*	truc;
//   for (int y = 0; y < size.Y; y += stride)
//     {
//       for (int x = 0; x < size.X; x += stride)
// 	{
// 	  FSceneView__SafeDeprojectFVector2D(SceneView, FVector2D(x, y),
// 					     WorldOrigin, WorldDirection);
// 	  if (World->LineTraceSingleByChannel(HitResult, WorldOrigin,
// 					      WorldOrigin + WorldDirection * 1000000.f,
// 					      ECollisionChannel::ECC_Visibility,
// 					      *CollisionQueryParams))
// 	    {
// 	      AActor*	Actor = HitResult.GetActor();
// 	      if (Actor != NULL)
// 		{
// 		  if (truc != Actor)
// 		    j += 50;
// 		  truc = Actor;
// 		  if (DidItWork == false)
// 		    UE_LOG(LogTemp, Warning, TEXT("SALUT"));
// 		  // for (int j = 0; j < objects.Num(); j++)
// 		  //   {
// 		  //     if (objects[j] == Actor)
// 		  // 	{

// 			  DidItWork = true;
// 			  for (int i = 0; i != 3; i += 1)
// 			    Result.Add(j + 1);
// 		      // 	  break;
// 		      // 	}
// 		      // else
// 		      // 	for (int i = 0; i != 3; i += 1)
// 		      // 	  Result.Add(0);
// 			  //}
// 		}
// 	      else
// 		{
// 		  for (int i = 0; i != 3; i += 1)
// 		    Result.Add(0);
// 		}
// 	    }
// 	  else
// 	    {
// 	      for (int i = 0; i != 3; i += 1)
// 		Result.Add(0);
// 	    }
// 	}
//     }
//   UE_LOG(LogTemp, Log, TEXT("number of pixels : %d"), Result.Num() / 3);
//   UE_LOG(LogTemp, Log, TEXT("\nWorldOrigin:%f/%f/%f\nWorldDirection:%f/%f/%f"), WorldOrigin.X, WorldOrigin.Y, WorldOrigin.Z, WorldDirection.X, WorldDirection.Y, WorldDirection.Z);

//   return (Result);
// }



/*
bool UtestScreenshot::CaptureDepthAndMasks(const FIntSize& size,
					   int stride, AActor* origin,
					   const TArray<AActor*>& objects,
					   const TArray<AActor*>& ignoredObjects,
					   TArray<FColor>& depth_data,
					   TArray<FColor>& mask_data)
{
  if (origin == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("origin is null"));
      return false;
    }
  UWorld*		World = origin->GetWorld();
  FSceneView*		SceneView = GetSceneView(UGameplayStatics::GetPlayerController(origin, 0), World);
  if (World == NULL || SceneView == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("SceneView or World are null"));
      return false;
    }
  float			HitResultTraceDistance = 100000.f;

  FVector		PlayerLoc  = origin->GetActorLocation();
  FRotator		PlayerRot = origin->GetActorRotation();
  FRotationMatrix	PlayerRotMat(PlayerRot);
  FVector		PlayerF = PlayerRotMat.GetScaledAxis(EAxis::X);
  PlayerF.Normalize();

  ECollisionChannel	TraceChannel = ECollisionChannel::ECC_Visibility;
  bool			bTraceComplex = false;
  FHitResult		HitResult;
  bool res = false;

  FCollisionQueryParams	CollisionQueryParams("ClickableTrace", bTraceComplex);
  for (auto& i : ignoredObjects)
    CollisionQueryParams.AddIgnoredActor(i);

  // Iterate over pixels
  for (int y = 0; y < size.Y; y+=stride)
    {
      for (int x = 0; x < size.X; x+=stride)
	{
	  FVector2D	ScreenPosition(x, y);
	  FVector	WorldOrigin, WorldDirection;
	  FSceneView__SafeDeprojectFVector2D(SceneView, ScreenPosition,
					     WorldOrigin, WorldDirection);
	  bool		bHit = World->LineTraceSingleByChannel(HitResult, WorldOrigin,
							       WorldOrigin + WorldDirection *
							       HitResultTraceDistance,
							       TraceChannel, CollisionQueryParams);

	  mask_data.Add(FColor(0)); // no foreground object
	  depth_data.Add(FColor(0));

	  if (bHit)
	    {
	      UE_LOG(LogTemp, Warning, TEXT("salut!"));
	      res = true;
	      // depth part
	      const auto &HitLoc = HitResult.Location;
	      AActor*	Actor = HitResult.GetActor();

	      FVector	HitLocRel = HitLoc - PlayerLoc;
	      float	DistToHit = FVector::DotProduct(HitLoc - PlayerLoc, PlayerF);
	      depth_data.Add(FColor(DistToHit));

	      // mask part
	      if (Actor != NULL)
		{
		  for (int i = 0; i < objects.Num(); i++)
		    {
		      if (objects[i] == Actor)
			{
			  mask_data.Add(FColor(i + 1));
			  break;
			}
		    }
		}
	    }
	}
    }
  return res;
}
*/
// static bool	SavePNG(const FIntSize& size, TArray<FColor>& data,
// 			std::string& path, int flag)
// {
//   path = path + (path.back() == '/' ? "" : "/") + "test_pictures";
//   DIR*		dir = opendir(path.c_str());
//   std::string	filename = buildFileName(flag);

//   if (!dir && ENOENT == errno)
//     {
//       if (mkdir(path.c_str(), S_IRUSR | S_IWUSR | S_IXUSR) == 0)
// 	{
// 	  UE_LOG(LogTemp, Log, TEXT("Created %s directory"), UTF8_TO_TCHAR(path.c_str()));
// 	  dir = opendir(path.c_str());
// 	}
//       else
// 	{
// 	  UE_LOG(LogTemp, Warning, TEXT("Cannot create %s directory: %s"),
// 		 UTF8_TO_TCHAR(path.c_str()), UTF8_TO_TCHAR(strerror(errno)));
// 	  return false;
// 	}
//     }
//   else if (!dir)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("opendir failed : %s"), UTF8_TO_TCHAR(strerror(errno)));
//       return false;
//     }
//   FILE	*fp;

//   if ((fp = fopen((path + "/" + filename).c_str(), "w+b")) == NULL)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("Cannot create %s file: %s"),
//   	     UTF8_TO_TCHAR((path + "/" + filename).c_str()), UTF8_TO_TCHAR(strerror(errno)));
//       return false;
//     }
//   fclose(fp);
//   png::image< png::rgb_pixel > image(128, 128);

//   for (png::uint_32 y = 0; y < image.get_height(); ++y)
//     {
//       for (png::uint_32 x = 0; x < image.get_width(); ++x)
//   	{
//   	  image[y][x] = png::rgb_pixel(x, y, x + y);
//   	  // non-checking equivalent of image.set_pixel(x, y, ...);
//   	}
//     }
//   image.write(path + "/" + filename);

//   // PNG WRITER
//   // png_structp	png_ptr = NULL;
//   // if ((png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING,
//   // 					 NULL, NULL, NULL)) == NULL)
//   //   UE_LOG(LogTemp, Warning, TEXT("Machin failed"));
//   // png_infop	info_ptr = png_create_info_struct(png_ptr);
//   // png_init_io(png_ptr, fp);

//   // /* write header */
//   // int bit_depth = 16;
//   // int color_type = PNG_COLOR_TYPE_RGB;
//   // png_set_IHDR(png_ptr, info_ptr, size.X, size.Y,
//   // 	       bit_depth, color_type, PNG_INTERLACE_NONE,
//   // 	       PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);

//   // png_write_info(png_ptr, info_ptr);
//   // /* write bytes */
//   // png_bytep*	row_pointers = NULL;
//   // if ((row_pointers = static_cast<unsigned char **>(malloc(sizeof(png_bytep)
//   // 							   * (size.Y + 1)))) == NULL)
//   //   UE_LOG(LogTemp, Fatal, TEXT("Malloc failed"));
//   // for (int y = 0; y < size.Y; y++)
//   //   {
//   //     png_bytep row;
//   //     if ((row = static_cast<unsigned char *>(malloc(sizeof(png_byte)
//   // 							* (size.X + 1)))) == NULL)
//   // 	UE_LOG(LogTemp, Fatal, TEXT("Malloc failed"));
//   //     row_pointers[y] = row;
//   //     for (int x = 0; x < size.X; x++)
//   // 	{
//   // 	  *row++ = data[(y * size.X) + x].R;
//   // 	  *row++ = data[(y * size.X) + x].G;
//   // 	  *row++ = data[(y * size.X) + x].B;
//   // 	}
//   //   }
//   // row_pointers[size.Y] = NULL;
//   // png_write_image(png_ptr, row_pointers);
//   // png_write_end(png_ptr, NULL);
//   // /* cleanup heap allocation */
//   // for (int y = 0; y < size.Y; y++)
//   //   free(row_pointers[y]);
//   // free(row_pointers);
//   // fclose(fp);
//   UE_LOG(LogTemp, Log, TEXT("Created picture %s in %s directory"),
// 	 UTF8_TO_TCHAR(filename.c_str()), UTF8_TO_TCHAR(path.c_str()));
//   return true;
// }

// bool	UtestScreenshot::DoTheWholeStuff(const FIntSize& size, int stride,
// 					 AActor* origin,
// 					 const TArray<AActor*>& objects,
// 					 const TArray<AActor*>& ignoredObjects)
// {
//   try {
//   // char			szTmp[32];
//   // int			len = 0;
//   // char*			pBuf = NULL;
//   // sprintf(szTmp, "/proc/%d/exe", getpid());
//   // int			bytes;
//   // bytes = readlink(szTmp, pBuf, len) < len - 1 ?
//   // 				       readlink(szTmp, pBuf, len) : len - 1;
//   // if (bytes >= 0)
//   //   pBuf[bytes] = '\0';
//   // std::string		path(pBuf);
//   std::string		path("/home/erwan/Images/ue/");
//   TArray<FColor>	screenshot;
//   TArray<FColor>	depth_data;
//   TArray<FColor>	mask_data;

//   if (origin == NULL)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("origin is NULL"));
//       return false;
//     }
//   if (UtestScreenshot::CaptureScreenshot(size, screenshot) == false)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("CaptureScreenshot failed"));
//       return false;
//     }
//   SavePNG(size, screenshot, path, 1);
//   // if (UtestScreenshot::CaptureDepthAndMasks(size, stride, origin, objects,
//   // 					    ignoredObjects, depth_data,
//   // 					    mask_data) == false)
//   //   {
//   //     UE_LOG(LogTemp, Warning, TEXT("CaptureDepthAndMask failed"));
//   //     return false;
//   //   }
//   // SavePNG(size, depth_data, path, 2);
//   // SavePNG(size, mask_data, path, 3);
//   }
//   catch (std::exception& e) {
//     std::string error = e.what();
//     UE_LOG(LogTemp, Warning, TEXT("%s"), error.c_str());
//   }
//   return true;
// }

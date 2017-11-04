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

void	UtestScreenshot::salut(const TArray<AActor*>& objects)
{
  UE_LOG(LogTemp, Warning, TEXT("Salut !"));
}

AActor*	UtestScreenshot::GetCamera(UWorld* world)
{
  return (world->GetFirstPlayerController());
}

static FSceneView*	GetSceneView(APlayerController* PlayerController, UWorld* World)
{
  if (GEngine == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("GEngine null"));
      return NULL;
    }
  if (GEngine->GameViewport == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("GameViewport null"));
      return NULL;
    }
  if (GEngine->GameViewport->Viewport == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("Viewport null"));
      return NULL;
    }
  auto Viewport = GEngine->GameViewport->Viewport;

  // Create a view family for the game viewport
  FSceneViewFamilyContext ViewFamily(FSceneViewFamily::ConstructionValues(Viewport,
									  World->Scene,
									  GEngine->GameViewport->EngineShowFlags).SetRealtimeUpdate(true));

  // Calculate a view where the player is to update the streaming from the players start location
  FVector		ViewLocation;
  FRotator		ViewRotation;
  ULocalPlayer*		LocalPlayer = Cast<ULocalPlayer>(PlayerController->Player);
  if (LocalPlayer == NULL)
    return NULL;
  FSceneView*		SceneView = LocalPlayer->CalcSceneView(&ViewFamily, /*out*/ ViewLocation,
							       /*out*/ ViewRotation, Viewport);
  return SceneView;
}

static void	FSceneView__SafeDeprojectFVector2D(const FSceneView* SceneView,
						   const FVector2D& ScreenPos,
						   FVector& out_WorldOrigin,
						   FVector& out_WorldDirection)
{
  const FMatrix	InverseViewMatrix = SceneView->ViewMatrices.GetViewMatrix().Inverse();
  const FMatrix	InvProjectionMatrix = SceneView->ViewMatrices.GetInvViewMatrix();

  SceneView->DeprojectScreenToWorld(ScreenPos, SceneView->UnscaledViewRect,
				    InverseViewMatrix, InvProjectionMatrix,
				    out_WorldOrigin, out_WorldDirection);
}

TArray<int>	UtestScreenshot::CaptureDepth(const FIntSize& size, int stride, AActor* origin,
					      const TArray<AActor*>& objects,
					      const TArray<AActor*>& ignoredObjects)
{
  TArray<int>		Result;
  TArray<FColor>	depth_data;
  if (origin == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("origin is null"));
      return Result;
    }
  UWorld*		World = origin->GetWorld();
  FSceneView*		SceneView = GetSceneView(UGameplayStatics::GetPlayerController(origin, 0), World);
  if (World == NULL || SceneView == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("SceneView or World are null"));
      return Result;
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

  FCollisionQueryParams	CollisionQueryParams("ClickableTrace", bTraceComplex);
  for (auto& i : ignoredObjects)
    CollisionQueryParams.AddIgnoredActor(i);

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

	  depth_data.Add(FColor(0));

	  if (bHit)
	    {
	      const auto &HitLoc = HitResult.Location;
	      AActor*	Actor = HitResult.GetActor();

	      FVector	HitLocRel = HitLoc - PlayerLoc;
	      float	DistToHit = FVector::DotProduct(HitLoc - PlayerLoc, PlayerF);
	      depth_data.Add(FColor(DistToHit));
	    }
	}
    }
  for(FColor color : depth_data) {
    Result.Add(color.R);
    Result.Add(color.G);
    Result.Add(color.B);
  }
  UE_LOG(LogTemp, Log, TEXT("number of pixels : %d"), depth_data.Num());
  return (Result);
}

TArray<int>	UtestScreenshot::CaptureMask(const FIntSize& size, int stride, AActor* origin,
					      const TArray<AActor*>& objects,
					      const TArray<AActor*>& ignoredObjects)
{
  TArray<int>		Result;
  TArray<FColor>	mask_data;
  if (origin == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("origin is null"));
      return Result;
    }
  UWorld*		World = origin->GetWorld();
  FSceneView*		SceneView = GetSceneView(UGameplayStatics::GetPlayerController(origin, 0), World);
  if (World == NULL || SceneView == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("SceneView or World are null"));
      return Result;
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

  FCollisionQueryParams	CollisionQueryParams("ClickableTrace", bTraceComplex);
  for (auto& i : ignoredObjects)
    CollisionQueryParams.AddIgnoredActor(i);

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

	  if (bHit)
	    {
	      // depth part
	      const auto &HitLoc = HitResult.Location;
	      AActor*	Actor = HitResult.GetActor();
	      FVector	HitLocRel = HitLoc - PlayerLoc;
	      float	DistToHit = FVector::DotProduct(HitLoc - PlayerLoc, PlayerF);
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
  for(FColor color : mask_data) {
    Result.Add(color.R);
    Result.Add(color.G);
    Result.Add(color.B);
  }
  UE_LOG(LogTemp, Log, TEXT("number of pixels : %d"), mask_data.Num());
  return Result;
}

TArray<int>		UtestScreenshot::CaptureScreenshot(const FIntSize& givenSize)
{
  TArray<int>		Result;
  TArray<FColor>	Bitmap;

  if (GEngine == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("GEngine null"));
      return Result;
    }
  if (GEngine->GameViewport == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("GameViewport null"));
      return Result;
    }
  if (GEngine->GameViewport->Viewport == NULL)
    {
      UE_LOG(LogTemp, Warning, TEXT("Viewport null"));
      return Result;
    }

  FViewport*		Viewport = GEngine->GameViewport->Viewport;

  if (givenSize.X != Viewport->GetSizeXY().X || givenSize.Y != Viewport->GetSizeXY().Y)
    {
      UE_LOG(LogTemp, Warning, TEXT("Viewport size : %d * %d\nSend size : %d * %d"), Viewport->GetSizeXY().X, Viewport->GetSizeXY().Y, givenSize.X, givenSize.Y);
      return Result;
    }
  TSharedPtr<SWindow>	WindowPtr = GEngine->GameViewport->GetWindow();

  bool			bScreenshotSuccessful = false;

  if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
    {
      // going here
      FIntVector	returnedSize(givenSize.X, givenSize.Y, 0);
      TSharedRef<SWidget> WindowRef = WindowPtr.ToSharedRef();
      bScreenshotSuccessful = FSlateApplication::Get().
  	TakeScreenshot(WindowRef, Bitmap, returnedSize);
      UE_LOG(LogTemp, Log, TEXT("returned size : %d * %d"), returnedSize.X, returnedSize.Y);
    }
  else // to be honnest I don't even know why this need to be here... As far as I know it's never used
    {
      FIntRect		Rect(0, 0, givenSize.X, givenSize.Y);
      bScreenshotSuccessful = GetViewportScreenShot(Viewport, Bitmap, Rect);
    }
  for(FColor color : Bitmap) {
    Result.Add(color.R);
    Result.Add(color.G);
    Result.Add(color.B);
  }
  UE_LOG(LogTemp, Log, TEXT("number of pixels : %d"), Bitmap.Num());
  return Result;
}

// the filename format will be, for instance, screenshot_%day-%month-%year_%hour:%minute:%second
FString		UtestScreenshot::BuildFileName(int flag)
{
  time_t	rawtime;
  struct tm *	timeinfo;
  char		buffer[25];

  time(&rawtime);
  timeinfo = localtime(&rawtime);
  strftime(buffer,sizeof(buffer),"%d-%m-%Y_%I:%M:%S",timeinfo);
  std::string str(buffer);
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
    }
  return (UTF8_TO_TCHAR(str.c_str()));
}


// bool UtestScreenshot::CaptureDepthAndMasks(const FIntSize& size,
// 					   int stride, AActor* origin,
// 					   const TArray<AActor*>& objects,
// 					   const TArray<AActor*>& ignoredObjects,
// 					   TArray<FColor>& depth_data,
// 					   TArray<FColor>& mask_data)
// {
//   if (origin == NULL)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("origin is null"));
//       return false;
//     }
//   UWorld*		World = origin->GetWorld();
//   FSceneView*		SceneView = GetSceneView(UGameplayStatics::GetPlayerController(origin, 0), World);
//   if (World == NULL || SceneView == NULL)
//     {
//       UE_LOG(LogTemp, Warning, TEXT("SceneView or World are null"));
//       return false;
//     }
//   float			HitResultTraceDistance = 100000.f;

//   FVector		PlayerLoc  = origin->GetActorLocation();
//   FRotator		PlayerRot = origin->GetActorRotation();
//   FRotationMatrix	PlayerRotMat(PlayerRot);
//   FVector		PlayerF = PlayerRotMat.GetScaledAxis(EAxis::X);
//   PlayerF.Normalize();

//   ECollisionChannel	TraceChannel = ECollisionChannel::ECC_Visibility;
//   bool			bTraceComplex = false;
//   FHitResult		HitResult;

//   FCollisionQueryParams	CollisionQueryParams("ClickableTrace", bTraceComplex);
//   for (auto& i : ignoredObjects)
//     CollisionQueryParams.AddIgnoredActor(i);

//   // Iterate over pixels
//   for (int y = 0; y < size.Y; y+=stride)
//     {
//       for (int x = 0; x < size.X; x+=stride)
// 	{
// 	  FVector2D	ScreenPosition(x, y);
// 	  FVector	WorldOrigin, WorldDirection;
// 	  FSceneView__SafeDeprojectFVector2D(SceneView, ScreenPosition,
// 					     WorldOrigin, WorldDirection);
// 	  bool		bHit = World->LineTraceSingleByChannel(HitResult, WorldOrigin,
// 							       WorldOrigin + WorldDirection *
// 							       HitResultTraceDistance,
// 							       TraceChannel, CollisionQueryParams);

// 	  mask_data.Add(FColor(0)); // no foreground object
// 	  depth_data.Add(FColor(0));

// 	  if (bHit)
// 	    {
// 	      // depth part
// 	      const auto &HitLoc = HitResult.Location;
// 	      AActor*	Actor = HitResult.GetActor();

// 	      FVector	HitLocRel = HitLoc - PlayerLoc;
// 	      float	DistToHit = FVector::DotProduct(HitLoc - PlayerLoc, PlayerF);
// 	      depth_data.Add(FColor(DistToHit));

// 	      // mask part
// 	      if (Actor != NULL)
// 		{
// 		  for (int i = 0; i < objects.Num(); i++)
// 		    {
// 		      if (objects[i] == Actor)
// 			{
// 			  mask_data.Add(FColor(i + 1));
// 			  break;
// 			}
// 		    }
// 		}
// 	    }
// 	}
//     }
//   return true;
// }

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

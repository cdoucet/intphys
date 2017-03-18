// Copyright 2016, 2017 Mario Ynocente Castro, Mathieu Bernard.

#include "NaivePhysics.h"
#include "NaivePhysicsLib.h"


UMaterialInterface* UNaivePhysicsLib::GetMaterial(const FString& Name)
{
    FString Prefix;
    FString Suffix;
    if(! Name.Split(FString(TEXT("/")), &Prefix, &Suffix, ESearchCase::IgnoreCase, ESearchDir::FromEnd))
    {
        return NULL;
    }

    FString Path = FString(TEXT("Material'/Game/Materials/"))
        + Name + FString(TEXT(".")) + Suffix + FString(TEXT("'"));

    return LoadObject<UMaterialInterface>(nullptr, Path.GetCharArray().GetData());
}

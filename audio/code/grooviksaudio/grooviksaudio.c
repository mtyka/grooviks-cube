#include "../fmodapi/inc/fmod.h"
#include "../fmodapi/inc/fmod_event.h"
#include "../fmodapi/inc/fmodlinux.h"
#include "../fmodapi/inc/fmod_errors.h"
#include "../../Grooviks Build Directory/grooviks.h"
#include <stdio.h>
#include <unistd.h>

void ERRCHECK(FMOD_RESULT result)
{
    if (result != FMOD_OK)
    {
        printf("FMOD error! (%d) %s\n", result, FMOD_ErrorString(result));
        exit(-1);
    }
}

FMOD_EVENTSYSTEM* Init()
{
    FMOD_EVENTSYSTEM *eventsystem;
    FMOD_RESULT       result;
    FMOD_SYSTEM      *system;
    FMOD_EVENTPROJECT      *project;
    int               key;
    unsigned int      version;

    /*
        Create a System object and initialize.
    */
    ERRCHECK(result = FMOD_EventSystem_Create(&eventsystem));
    ERRCHECK(result = FMOD_EventSystem_GetSystemObject(eventsystem, &system));
    ERRCHECK(result = FMOD_EventSystem_Init(eventsystem, 256, FMOD_INIT_NORMAL, 0, FMOD_EVENT_INIT_USE_GUIDS));
    ERRCHECK(result = FMOD_System_GetVersion(system, &version));

  if (version < FMOD_VERSION)
    {
        printf("Error!  You are using an old version of FMOD %08x.  This program requires %08x\n", version, FMOD_VERSION);
        return 0;
    }
    printf("Setting media path\n"); 
    ERRCHECK(result = FMOD_EventSystem_SetMediaPath(eventsystem, "media/"));
    printf("loading fev\n");
    ERRCHECK(result = FMOD_EventSystem_Load(eventsystem, "grooviks.fev", 0, &project));

    return eventsystem;
}

void PlayStoneSound(FMOD_EVENTSYSTEM *eventsystem)
{
    FMOD_EVENT *event; 
    FMOD_RESULT       result;
    printf("loading event\n");
    ERRCHECK(result = FMOD_EventSystem_GetEventByGUIDString(eventsystem, EVENTGUID_GROOVIKS_UNTITLED_STONE_GEARS, FMOD_EVENT_DEFAULT, &event));

    ERRCHECK(result = FMOD_Event_Start(event)); 
    ERRCHECK(result = FMOD_EventSystem_Update(eventsystem));
}

void Close(FMOD_EVENTSYSTEM *eventsystem)
{
    FMOD_SYSTEM      *system;
    FMOD_RESULT       result;

    ERRCHECK(result = FMOD_EventSystem_GetSystemObject(eventsystem, &system));
    ERRCHECK(result = FMOD_EventSystem_Unload(eventsystem));
    ERRCHECK(result = FMOD_System_Close(system));
    ERRCHECK(result = FMOD_System_Release(system));
}
 

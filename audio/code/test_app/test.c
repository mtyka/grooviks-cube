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

int main(int argc, char * argv[])
{
    FMOD_SYSTEM      *system;
    FMOD_EVENTSYSTEM *eventsystem;
    FMOD_SOUND       *sound1, *sound2, *sound3;
    FMOD_CHANNEL     *channel = 0;
    FMOD_RESULT       result;
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
    ERRCHECK(result = FMOD_EventSystem_SetMediaPath(eventsystem, "../../Grooviks\ Build\ Directory/"));
    printf("loading fev\n");
    ERRCHECK(result = FMOD_EventSystem_Load(eventsystem, "grooviks.fev", 0, &project));
    
    FMOD_EVENT *event; 
    printf("loading event\n");
    ERRCHECK(result = FMOD_EventSystem_GetEventByGUIDString(eventsystem, EVENTGUID_GROOVIKS_UNTITLED_STONE_GEARS, FMOD_EVENT_DEFAULT, &event));

   ERRCHECK(result = FMOD_Event_Start(event)); 
    ERRCHECK(result = FMOD_EventSystem_Update(eventsystem));
    sleep(2);
    FMOD_EventSystem_Unload(eventsystem);
    result = FMOD_System_Close(system);
    result = FMOD_System_Release(system);
    return 0;
}

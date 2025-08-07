
#ifdef __GNUC__

#include <sys/time.h>
int GetTickCount(void) {
  timeval t;
  gettimeofday( &t, 0 );
  return t.tv_sec*1000 + t.tv_usec/1000;
}

#else

extern "C" __declspec(dllimport) uint __stdcall GetTickCount( void );

#endif

//extern "C" __declspec(dllimport) void __stdcall Sleep( uint );

//extern "C" __declspec(dllimport) uint __stdcall GetTickCount( void );

uint starttick,lasttick,curtick,fintick;

#define StartTimer() (starttick=lasttick=GetTickCount())
//#define StartTimer(xxx) (starttick=GetTickCount(),lasttick=starttick+xxx)

#define CheckTimer(xxx) (curtick=GetTickCount(),(lasttick<=curtick)?lasttick=curtick+(xxx),1:0)

#define BreakTimer() (fintick=GetTickCount()-starttick)

#define PrintTimer() (printf("%i.%03is",fintick/1000,fintick%1000))

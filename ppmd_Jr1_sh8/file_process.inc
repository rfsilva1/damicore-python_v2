
void PrintInfo( FILE* f, FILE* g, int iram ) {
  double fn = ftell(f);
  double gn = ftell(g);
  float ram = iram;
  float bpb = fn>0 ? 8*gn/fn : 8;
  double tm = curtick-starttick; tm/=1000;
  float sp = tm>0 ? fn/tm/1024 : 0;
  if( Mode ) SWAP( fn, gn );
  printf( " %.0lf > %.0lf, %4.2f bpb, %6.1fM RAM, %4.0fKb/s\r", fn,gn, bpb, ram/(1<<20), sp );
  fflush(stdout);
}

#include "E89_v2a.inc"
exefilter e89;

template< int DECODE, int UseE8, class Rangecoder >
void ProcessFile(
  Rangecoder& rc,
  FILE* DecodedFile,
  FILE* EncodedFile,
  int MaxOrder, int CutOff
) {
  int i;

  rc.io.CodeFile = EncodedFile;
//  rc.ProcMode = DECODE;
  rc.Init();

  model.Init( MaxOrder );

  StartTimer();
  for( i=0; i<SrcLen; i++ ) {
    int c=0;

    if( !DECODE ) {
      if( UseE8 ) {
        do { c = e89.forward( getc(DecodedFile) ); } while( c<0 );
      } else {
        c = getc(DecodedFile);
      }
    }

    if( !model.ProcessByte<DECODE>(rc,c) ) {
      // || GetUsedMemory()<(SubAllocatorSize>>2)
      if( CutOff ) {
        model.RestoreModelRare();
      } else {
        model.StartModelRare();
      }
    }

    if( (byte(i)==0) && CheckTimer(500) ) {
      if( Silent ) PrintInfo( DecodedFile, EncodedFile, model.GetUsedMemory() );
    }

    if( DECODE ) {
      if( UseE8 ) {
        c = e89.inverse( c );
        if( c>=0 ) putc( c, DecodedFile );
      } else {
        putc( c, DecodedFile );
      }
    }
  }

  int lastram = lastram=model.GetUsedMemory();
  model.Quit();

  rc.Quit();

  if( DECODE && UseE8 ) {
    int c;
    while( (c=e89.flush())>=0 ) putc( c, DecodedFile );
  }

  if( Silent ) {
    BreakTimer();
    PrintInfo( DecodedFile, EncodedFile, lastram );
    printf( "\nProcessing time: " ); PrintTimer();
    printf( "\n" );
  }

}

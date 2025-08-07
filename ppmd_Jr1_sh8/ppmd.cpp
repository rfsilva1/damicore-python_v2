#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

typedef unsigned short word;
typedef unsigned int   uint;
typedef unsigned char  byte;
typedef unsigned long long qword;
typedef int BOOL;

int Mode=0;   // encoding
int Silent=1; // print all

//int UseE8=1;
//int f_CutOff=0;
//int RCType=0;
struct {
  uint UseE8   :1;
  uint CutOff  :1;
  uint RCType  :1;
} FLAGS = { 1, 0, 0 };

const int ORealMAX=256;
int OMAX=16;
int MMAX=256;
uint SrcLen;

#include "timer.inc"

#include "sh_v1m.inc"
#include "sh_v1x.inc"

#include "model.inc"

Model model;

#include "file_process.inc"

uint flen( FILE* f ) {
  fseek( f, 0, SEEK_END );
  uint len = ftell(f);
  fseek( f, 0, SEEK_SET );
  return len;
}

template< class var >
void fprocess( var& x, int l, FILE* f ) {
  if( Mode ) {
    //x = 0;
    memset( &x, 0, sizeof(x) );
    fread( &x, 1,l, f );
  } else {
    fwrite( &x,1,l, f );
  }
}




#include "def_date.inc"

char logo[256];

__attribute__((noreturn))
void PrintError( char* s ) {
  if( Silent) printf( logo );
  printf( s );
  exit(0);
}


template< class Rangecoder0, class Rangecoder1 >
void Switch_ProcessFile( FILE* Source, FILE* Target ) {
  if( Mode ) {
    Rangecoder1 rc;
    FLAGS.UseE8 ?
      ProcessFile<1,1>( rc, Source, Target, OMAX, FLAGS.CutOff )
    : ProcessFile<1,0>( rc, Source, Target, OMAX, FLAGS.CutOff );
  } else {
    Rangecoder0 rc;
    FLAGS.UseE8 ?
      ProcessFile<0,1>( rc, Source, Target, OMAX, FLAGS.CutOff )
    : ProcessFile<0,0>( rc, Source, Target, OMAX, FLAGS.CutOff );
  }
}


int main( int argc, char** argv ) {

  sprintf( logo, "PPMd Jr1 (c) 2006 Dmitry Shkarin\n"
                 "Revision sh8 by Eugene D. Shelwien [%s]\n", __DATE__ );

  int i,j,k; char temp[256];
  FILE* Source;
  FILE* Target;

  while(1) {

    if( argc<2 ) {
      PrintError(
      "Usage: ppmd [options] <source> [<destination>]\n\n"
      "/c,/c0 - encode <source> into <destination> (default)\n"
      "/c1    - encode <source> into <destination> with faster rangecoder\n"
      "/d     - decode <source> into <destination>\n"
      "/o#    - Model order selection (0..1024)\n"
      "/m#    - Dictionary size in megabytes (1..4000)\n"
      "/e     - Disable E8 filter\n"
      "/r     - Use model cutoff instead of fast flush\n"
      "/q     - No messages\n"
      );
    }

    if( argv[1][0]=='/' ) {
      char option = argv[1][1];
      k = atoi( &argv[1][2] );
      switch( option & 0xDF ) {
        case 'C': Mode = 0; FLAGS.RCType=(k>0); break;
        case 'D': Mode = 1;  break;
        case 'E': FLAGS.UseE8 = 0; break;
        case 'R': FLAGS.CutOff = 1; break;
        case 'O': if( k<0 || k>ORealMAX ) PrintError( "Invalid order setting.\n" );
                  OMAX = k; break;
        case 'M': if( k<1 || k>4000 ) PrintError( "Invalid dictionary size setting.\n" );
                  MMAX = k; break;
        case 'Q': Silent = 0; break;
        default:  PrintError( "Invalid option.\n" );
      }
      for( i=2; i<argc; i++ ) argv[i-1]=argv[i];
      argc--;
      continue;
    }

    Source = fopen( argv[1], "rb" );
    if( !Source ) PrintError( "Cannot open source file.\n" );

    strcpy( temp, argv[1] );
    for(
      k=j=strlen(temp), i=j-1;
      i>=0 && temp[i]!='\\' && temp[i]!='/' && temp[i]!=':'
           && (temp[i]!='.' || (j=(j<k)?j:i,1) );
      i--
    );

    strcpy( &temp[j], Mode ? ".unp" : ".pmd" );
    strcpy( temp, &temp[i+1] );

    if( argc>2 ) strcpy( temp, argv[2] );

    Target = fopen( temp, "wb" );
    if( !Target ) PrintError("Cannot create output file.\n");

    break;

  };

  PPMD_STARTUP();

  if( Mode==0 ) SrcLen = flen(Source); else SWAP( Source, Target );

  fprocess( SrcLen, 4, Target );
  fprocess( OMAX,   2, Target );
  fprocess( MMAX,   2, Target );
  fprocess( FLAGS,  1, Target );

  if( !model.StartSubAllocator( MMAX ) ) return 1;

  if( Silent ) {
    char* s[] = { "En", "De" };
    printf( "%s \xfe %scoding...\n"
            " \xfe  Input file: \042%s\042\n"
            " \xfe Output file: \042%s\042\n", logo, s[Mode], argv[1], temp );
    printf( " \xfe Model order %i, %iM for statistics. ", OMAX, MMAX );
    if( FLAGS.UseE8 )  printf( "E8 enabled. " );
    if( FLAGS.CutOff ) printf( "Model cutoff. " );
    if( FLAGS.RCType ) printf( "RC=SH1x." );
    printf( "\n" );
  }

  if( FLAGS.RCType==0 ) {
    Switch_ProcessFile< Rangecoder_SH1m<0>, Rangecoder_SH1m<1> >( Source, Target );
  } else {
    Switch_ProcessFile< Rangecoder_SH1x<0>, Rangecoder_SH1x<1> >( Source, Target );
  }

  return 0;
}

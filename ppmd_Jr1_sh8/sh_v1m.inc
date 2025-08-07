
template< int ProcMode >
struct Rangecoder_SH1m {

  enum {
    SCALElog = 15,
    SCALE    = 1<<SCALElog
  };

  enum {
    NUM   = 4,
    sTOP  = 0x01000000U,
    Thres = 0xFF000000U
  };

//  int   ProcMode; // 0=encode, 1=decode;
  union {
    struct {
      uint  low;
      uint  Carry;
    };
    qword lowc;
  };
  uint  code;
  uint  FFNum;
  uint  Cache;
  uint  range;

  struct DefaultIO {
    FILE* CodeFile;
    unsigned char get(void) { return getc(CodeFile); }
    void put( int c ) { putc( c, CodeFile ); }
  };
  DefaultIO io;
  unsigned char get(void) { return io.get(); }
  void put( int c ) { io.put(c); }


  uint muldivR( uint a, uint b ) { return (qword(a)*b)/range; }

  uint mulRdiv( uint a, uint c ) { return (qword(a)*range)/c; }

  void Process( uint cumFreq, uint freq, uint totFreq ) {
    uint tmp = mulRdiv( cumFreq, totFreq ) + 1;
    if( ProcMode ) code-=tmp; else lowc+=tmp;
    range = mulRdiv( cumFreq+freq, totFreq ) - tmp;
    if( ProcMode )
      while( range<sTOP ) range<<=8, (code<<=8)+=get();
    else
      while( range<sTOP ) range<<=8, ShiftLow();
  }


  void Arrange( uint totFreq ) {}

  uint GetFreq( uint totFreq ) {
    return muldivR( code, totFreq );
  }


  void BProcess( uint freq, int& bit ) {
    int x[] = { 0, freq, SCALE };
    if( ProcMode ) {
      uint count = GetFreq( SCALE );
      bit = (count>=freq);
    }
    Process( x[bit], x[1+bit]-x[bit], SCALE );
  }

  void ShiftLow( void ) {
    if( low<Thres || Carry ) {
      put( Cache+Carry );
      for (;FFNum != 0;FFNum--) put( Carry-1 ); // (Carry-1)&255;
      Cache = low>>24;
      Carry = 0;
    } else FFNum++;
    low<<=8;
  }


  void rcInit( void ) {
    range = 0xFFFFFFFF;
    low   = 0;
    FFNum = 0;
    Carry = 0;
    Cache = 0;
  }

  void Init( void ) {
    rcInit();
    if( ProcMode==1 ) {
      for(int _=0; _<NUM+1; _++) (code<<=8)+=get();
    }
  }

  void Quit( void ) {
    if( ProcMode==0 ) {
      for(int _=0; _<NUM+1; _++) ShiftLow();
    }
  }

};

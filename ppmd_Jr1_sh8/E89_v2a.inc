
struct exefilter {

  uint x0,x1;
  uint i,k;
  byte cs; // cache size, F8 - 5 bytes

  enum{
   winlog=24, winlog1=32-(winlog+1), winlog2=(winlog+1-8), window=1<<winlog,
   window0=window+(0<<20), window2=2*window,
   mwindow=window2-1, xwindow=((1<<winlog2)-1)
  };

  exefilter( void ) { init(); }

  void init( void ) {
    cs = 0xFF;
    x0 = x1 = 0;
    i  = 0;
    k  = 5;
  }

  int cache_byte( int c ) {
    int d = cs&0x80 ? -1 : byte(x1);
    (x1>>=8)|=(x0<<24);
    (x0>>=8)|=(c <<24);
    cs<<=1; i++;
    return d;
  }

  uint xswap( uint x ) { return x; }
  uint yswap( uint x ) { return x; }

/*
  uint xswap( uint x ) {
    int i; uint y;
    for( i=0; i<=winlog; i++ ) {
      y += y + (x&1); x>>=1;
    }
    return y;
  }

  #define yswap xswap
*/

/*
  uint xswap( uint x ) {
    return ((x&xwindow)<<8) | (x>>winlog2);
  }

  uint yswap( uint x ) {
    return (x>>8) | (byte(x)<<winlog2);
  }
*/

/*
  uint xswap( uint x ) {
    x<<=winlog1;
    return (x>>24)|(byte(x>>16)<<8)|(byte(x>>8)<<16)|(byte(x)<<(24-winlog1));
  }

  uint yswap( uint x ) {
    x = (byte(x>>24)<<winlog1)|(byte(x>>16)<<8)|(byte(x>>8)<<16)|(x<<24);
    return x>>winlog1;
  }
*/

  int forward( int c ) {
    if( i>=k ) {
      if( (x1&0xFF000000)==0xE8000000 ) {
        k = i+4;
        uint x = x0 + window0;
        if( (x<window2) && (c>=0) ) {
          x = (x+i) & mwindow;
          x = xswap(x);
          x0 = x - window0;
        }
      }
    }
    return cache_byte(c);
  }

  int inverse( int c ) {
    if( i>=k ) {
      if( (x1&0xFF000000)==0xE8000000 ) {
        k = i+4;
        uint x = x0 + window0;
        if( x<window2 ) {
          x = yswap(x);
          x = (x-i) & mwindow;
          x0 = x - window0;
        }
      }
    }
    return cache_byte(c);
  }

  int flush() {
    if( cs!=0xFF ) {
      while( cs&0x80 ) cache_byte(0),++cs;
      int d = cache_byte(0); ++cs;
      return d;
    } else {
      init();
      return -1;
    }
  }


};


const int MAX_O=ORealMAX;  // maximum allowed model order

enum { FALSE=0,TRUE=1 };

template <class T>
  T CLAMP( const T& X, const T& LoX, const T& HiX ) { return (X >= LoX)?((X <= HiX)?(X):(HiX)):(LoX); }

template <class T>
  void SWAP( T& t1, T& t2 ) { T tmp=t1; t1=t2; t2=tmp; }

void PrefetchData(void* Addr) {
  byte Prefetchbyte = *(volatile byte*)Addr;
}

enum{
  UNIT_SIZE=12,
  N1=4, N2=4, N3=4, N4=(128+3-1*N1-2*N2-3*N3)/4,
  N_INDEXES=N1+N2+N3+N4
};

uint   Ptr2Indx(void* p) { return (uint)p; }
void*  Indx2Ptr(uint indx) { return (void*)indx; }

signed char EscCoef[12] = {
  16, -10, 1, 51, 14, 89, 23, 35, 64, 26, -42, 43
};

// Tabulated escapes for exponential symbol distribution
const byte ExpEscape[16]={51,43,18,12,11,9,8,7,6,5,4,3,3,2,2,2};

enum {
  UP_FREQ     = 5,
};

byte Indx2Units[N_INDEXES];
byte Units2Indx[128]; // constants

byte NS2BSIndx[256];
byte QTable[260];


// constants initialization
void PPMD_STARTUP( void ) {
  int i, k, m, Step;

  for( i=0,k=1; i<N1         ;i++,k+=1 ) Indx2Units[i]=k;
  for( k++;     i<N1+N2      ;i++,k+=2 ) Indx2Units[i]=k;
  for( k++;     i<N1+N2+N3   ;i++,k+=3 ) Indx2Units[i]=k;
  for( k++;     i<N1+N2+N3+N4;i++,k+=4 ) Indx2Units[i]=k;

  for( k=0,i=0; k<128; k++ ) {
    i += Indx2Units[i]<k+1;
    Units2Indx[k]=i;
  }

  NS2BSIndx[0] = 2*0;
  NS2BSIndx[1] = 2*1;
  NS2BSIndx[2] = 2*1;
  memset(NS2BSIndx+3,  2*2, 26);
  memset(NS2BSIndx+29, 2*3, 256-29);

  for( i=0; i<UP_FREQ; i++ ) QTable[i]=i;

  for( m=i=UP_FREQ, k=Step=1; i<260; i++ ) {
    QTable[i] = m;
    if( !--k ) k = ++Step, m++;
  }
}

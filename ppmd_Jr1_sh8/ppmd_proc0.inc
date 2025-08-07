
int  PrevSuccess;
word BinSumm[25][64]; // binary SEE-contexts

// encode in binary (deterministic) context
template< int DECODE, class Rangecoder >
void processBinSymbol( Rangecoder& rc, PPM_CONTEXT& q, int symbol ) {
  STATE& rs = q.oneState();
  int   i  = NS2BSIndx[q.suff()->NumStats] + PrevSuccess + q.Flags + ((RunLength>>26) & 0x20);
  word& bs = BinSumm[QTable[rs.Freq-1]][i];
  BSumm    = bs;
  bs      -= (BSumm+64) >> PERIOD_BITS;

  int flag = DECODE ? 0 : rs.Symbol!=symbol;
  rc.BProcess( BSumm+BSumm, flag );

  if( flag ) {
    CharMask[rs.Symbol] = EscCount;
    NumMasked = 0;
    PrevSuccess = 0;
    FoundState = 0;
  } else {
    bs += INTERVAL;
    rs.Freq += (rs.Freq<196);
    RunLength++;
    PrevSuccess = 1;
    FoundState = &rs;
  }
}


template< int DECODE, class Rangecoder >
PPM_CONTEXT* ProcessByte( Rangecoder& rc, int& c ) {

  PPM_CONTEXT* MinContext = MaxContext;
  if( MinContext->NumStats ) {
    processSymbol1<DECODE>(   rc, MinContext[0], c );
  } else {
    processBinSymbol<DECODE>( rc, MinContext[0], c );
  }

  while( !FoundState ) {
    do {
//        if( !MinContext->iSuffix ) { c=-1; return; };
      OrderFall++;
      MinContext = MinContext->suff();
    } while( MinContext->NumStats==NumMasked );
    processSymbol2<DECODE>( rc, MinContext[0], c );
  }

  if( DECODE ) c = FoundState->Symbol;

  PPM_CONTEXT* p;
  if( (OrderFall!=0) || ((byte*)FoundState->getSucc()<UnitsStart) ) {
    p = UpdateModel( MinContext );
    if( p ) MaxContext = p;
  } else {
    p = MaxContext = FoundState->getSucc();
  }

  return p;
}


#pragma pack(1)

#include "ppmd_init.inc"

#include "mod_context.inc"

struct Model {
  #include "alloc_node.inc"
  #include "alloc_units.inc"

  int _MaxOrder;
  int OrderFall;
  STATE* FoundState; // found next state transition
  PPM_CONTEXT* MaxContext;

  uint EscCount;
  uint CharMask[256];

  int  BSumm;
  int  RunLength;
  int  InitRL;

  #include "mod_see.inc"

  int  NumMasked;

  #include "mod_rescale.inc"
  #include "mod_cutoff.inc"

  #include "ppmd_flush.inc"
  #include "ppmd_update.inc"

  #include "ppmd_proc0.inc"
  #include "ppmd_proc1.inc"
  #include "ppmd_proc2.inc"

  void Init( int MaxOrder ) {
    _MaxOrder = MaxOrder;
    StartModelRare();
  }

  void Quit( void ) {
    StopSubAllocator();
  }

  #include "ppmd_byte.inc"

};

#pragma pack()

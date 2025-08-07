
uint  GlueCount;
uint  GlueCount1;
uint  SubAllocatorSize;
byte* HeapStart;
byte* pText;
byte* UnitsStart;
byte* LoUnit;
byte* HiUnit;
byte* AuxUnit;

struct _MEM_BLK {
  uint Stamp;
  uint NextIndx;
  uint NU;
};

struct BLK_NODE {
  uint Stamp;
  uint NextIndx;

  BLK_NODE* getNext() const {
    return (BLK_NODE*)Indx2Ptr(NextIndx);
  }

  void setNext(BLK_NODE* p) {
    NextIndx = Ptr2Indx(p);
  }

  int avail() const {
    return (NextIndx!=0);
  }

  void link( BLK_NODE* p ) {
    p->NextIndx = NextIndx;
    setNext( p );
  }

  void unlink() {
    NextIndx = getNext()->NextIndx;
  }

  void* remove() {
    BLK_NODE* p = getNext();
    unlink();
    Stamp--;
    return p;
  }

  void insert( void* pv, int NU ) {
    BLK_NODE* p = (BLK_NODE*)pv;
    link(p);
    p->Stamp = ~uint(0);
    ((_MEM_BLK&)*p).NU = NU;
    Stamp++;
  }
};

struct MEM_BLK : public BLK_NODE {
  uint NU;
};

typedef BLK_NODE* pBLK_NODE;

typedef MEM_BLK* pMEM_BLK;

BLK_NODE BList[N_INDEXES+1];

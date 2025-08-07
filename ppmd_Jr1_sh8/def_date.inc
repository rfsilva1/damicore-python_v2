
const int nummonth =
   __DATE__[0]=='D'?12
  :__DATE__[0]=='F'?2
  :__DATE__[0]=='N'?11
  :__DATE__[0]=='O'?10
  :__DATE__[0]=='S'?9
  :__DATE__[0]=='A'? __DATE__[1]=='p'?4:8
  :__DATE__[0]=='J'? __DATE__[1]=='a'?1: __DATE__[2]=='l'? 7:6
  :__DATE__[2]=='r'?3:5;

char __DATE[] = {
  (__DATE__[4]==' '?'0':__DATE__[4]),__DATE__[5], '.',
  (nummonth>9?'1':'0'),'0'+nummonth%10, '.',
  __DATE__[7],__DATE__[8],__DATE__[9],__DATE__[10],' ',
  __TIME__[0],__TIME__[1], ':',
  __TIME__[3],__TIME__[4], 0
};

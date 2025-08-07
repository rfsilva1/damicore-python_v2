@echo off

set ICLCFG=icl.cfg

del ppmd.exe
call C:\IntelB0074\IA32\Bin\icl.bat ppmd.cpp

del *.exp *.obj

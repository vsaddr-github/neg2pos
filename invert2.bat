echo on
:: Adjust path PYTH to your liking
set PYTH="C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe" 

%PYTH%  D:\GitHub\neg2pos\shape02.py  %1 > %TEMP%\c4c.txt
type %TEMP%\c4c.txt
%PYTH%  D:\GitHub\neg2pos\inv7.py %TEMP%\c4c.txt

pause 20
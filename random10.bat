@echo off
ECHO Avvio di 10 istanze parallele dello script run_random.py...

FOR /L %%i IN (1,1,10) DO (
    START "Processo %%i" cmd /c "python examples\run_random.py && ECHO Processo %%i Completato"
    timeout /t 1 /nobreak > nul
)

ECHO Tutte le 10 istanze sono state avviate.

PAUSE
@echo off

REM Run reco2text.py
python reco2text.py
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to run reco2text.py
    exit /b 1
)

REM Run text3faq.py
python text2faq.py
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to run text2faq.py
    exit /b 1
)

echo Both scripts ran successfully

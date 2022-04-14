SET PYTHON_EGG_CACHE=%~dp0virtualenv\egg_cache
call "%~dp0virtualenv\scripts\activate" || goto :error

goto :EOF

:error
exit /b %errorlevel%
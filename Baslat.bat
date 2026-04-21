@echo off
echo ==========================================
echo    OtoBilet - Uygulama Baslatiliyor
echo ==========================================

echo [1/3] Docker konteynerlari ayaga kaldiriliyor...
docker-compose up -d

echo [2/3] Servislerin hazirlanmasi bekleniyor (10 saniye)...
timeout /t 10 /nobreak > nul

echo [3/3] Tarayici aciliyor: http://localhost
start http://localhost

echo.
echo Uygulama basariyla acildi! 
echo Konteynerlar arka planda calismaya devam ediyor.
echo Kapatmak isterseniz Docker Desktop uzerinden durdurabilirsiniz.
echo.
pause

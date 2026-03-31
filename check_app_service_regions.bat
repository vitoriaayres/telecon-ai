@echo off
echo ========================================
echo   CHECKING AZURE APP SERVICE REGIONS
echo ========================================
echo.
echo This shows ALL regions where you can deploy App Service
echo (Much more than Static Web Apps!)
echo.
pause

az account show

echo.
echo Checking available App Service regions...
echo.

az appservice list-locations --sku FREE --linux-workers-enabled --output table

echo.
echo ========================================
echo These regions support App Service!
echo Pick ANY region from the list above
echo ========================================
echo.
pause

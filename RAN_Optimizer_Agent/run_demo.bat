@echo off
echo ================================================
echo RAN Network Optimizer - Web Demo Launcher
echo ================================================
echo.
echo Starting Streamlit web application...
echo.
echo The demo will open in your default browser.
echo Press Ctrl+C to stop the server.
echo.
echo ================================================
echo.

cd /d "%~dp0"
streamlit run web_demo.py

pause

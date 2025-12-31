@echo off
chcp 65001
title 🎤 Installation Zodiac Vocal

echo.
echo ╔══════════════════════════════════════╗
echo ║      🎤 ZODIAC v10.0 - Vocal         ║
echo ╚══════════════════════════════════════╝
echo.

echo 📦 Installation des dépendances vocales...
pip install SpeechRecognition pyttsx3 pyaudio
pip install psutil pyautogui

echo.
echo 🎯 Création des dossiers...
mkdir data 2>nul
mkdir logs 2>nul

echo.
echo ✅ Installation terminée !
echo.
echo 🎤 Pour utiliser Zodiac en mode vocal:
echo   1. python main.py
echo   2. Cliquez sur 🎤 ou dites "Zodiac"
echo.
echo 💡 Commandes vocales:
echo   • "Zodiac ouvre chrome"
echo   • "Zodiac musique suivante"
echo   • "Zodiac éteins l'écran"
echo.
pause
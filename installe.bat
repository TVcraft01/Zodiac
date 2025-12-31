@echo off
chcp 65001
title 🔐 Installation Zodiac Sécurisé

echo.
echo ╔══════════════════════════════════════╗
echo ║      🔐 ZODIAC v10.0 - Sécurisé      ║
echo ╚══════════════════════════════════════╝
echo.

echo 📦 Installation des dépendances...
pip install SpeechRecognition pyttsx3 pyaudio psutil pyautogui

echo.
echo 📁 Création des dossiers...
mkdir data 2>nul
mkdir core 2>nul
mkdir logs 2>nul

echo.
echo ✅ Installation terminée !
echo.
echo 🚀 Pour lancer Zodiac:
echo   python main.py
echo.
echo 🔒 À la première exécution:
echo   1. Zodiac scannera votre système
echo   2. TOUTES les apps seront bloquées par défaut
echo   3. Activez manuellement celles que vous voulez
echo.
pause
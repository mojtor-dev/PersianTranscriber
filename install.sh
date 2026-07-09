#!/data/data/com.termux/files/usr/bin/bash

clear

echo "========================================"
echo " PersianTranscriber Pro Installer"
echo " Version 2.0"
echo "========================================"
echo

check_package () {

if command -v "$1" >/dev/null 2>&1
then
    echo "[OK] $1 نصب است."
else
    echo "[INFO] نصب $1 ..."
    pkg install -y "$1"
fi

}

echo "بررسی اینترنت..."

if curl -Is https://www.google.com >/dev/null 2>&1
then
    echo "[OK] اینترنت برقرار است."
else
    echo "[خطا] اتصال اینترنت برقرار نیست."
    exit 1
fi

echo

check_package ffmpeg
check_package curl
check_package jq
check_package git
check_package python

echo

echo "بررسی دسترسی حافظه..."

if [ ! -d "$HOME/storage/shared" ]
then
    echo
    echo "دسترسی حافظه داده نشده."
    echo
    termux-setup-storage
    echo
    echo "بعد از تایید مجدداً install.sh را اجرا کن."
    exit
fi

echo "[OK] دسترسی حافظه برقرار است."

echo

if [ -z "$GROQ_API_KEY" ]
then
    echo "API Key پیدا نشد."
    echo
    echo "دستور زیر را اجرا کن:"
    echo
    echo 'echo export GROQ_API_KEY="YOUR_KEY" >> ~/.bashrc'
else
    echo "[OK] API Key پیدا شد."
fi

echo
echo "======================================"
echo "نصب اولیه کامل شد."
echo "======================================"



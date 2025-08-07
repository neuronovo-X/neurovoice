# Нейро-Голос
<img width="1279" height="842" alt="2212" src="https://github.com/user-attachments/assets/3e885c19-5c3e-40fd-872f-d26976abec4b" />

Генерация озвучки текста с помощью Microsoft Edge TTS (streamlit web-интерфейс).

## Возможности
- Озвучка текста на английском и русском языках
- Поддержка мужских и женских голосов
- Регулировка скорости и громкости
- Скачивание результата в формате WAV

## Запуск
1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
2. Запустите приложение:
   ```
   streamlit run app.py
   ```
   или используйте скрипт `start.bat` (Windows).

## Требования
- Python 3.8+
- ffmpeg (для работы pydub)

## Разработчик
Автор: Нейроново

---

**Для связи:** https://t.me/neuronovo или https://github.com/neuronovo-X

## ⚠️ Disclaimer

This project uses the publicly available Microsoft Edge TTS service through the `edge-tts` library.

All rights to the voices and audio content belong to Microsoft.  
This tool is intended for educational and non-commercial purposes only.

The author of this repository is not affiliated with Microsoft.

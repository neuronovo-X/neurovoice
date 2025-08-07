import streamlit as st
import os
import tempfile
import asyncio
import uuid

try:
    import edge_tts
except ImportError:
    st.error("Модуль edge-tts не установлен! Установите командой: pip install edge-tts")
    st.stop()
try:
    from pydub import AudioSegment
    from pydub.utils import which
except ImportError:
    st.error("Модуль pydub не установлен! Установите командой: pip install pydub")
    st.stop()

# Корректная проверка ffmpeg
if not which("ffmpeg"):
    st.warning("Внимание: ffmpeg не найден! Pydub не сможет объединять WAV. Скачайте ffmpeg и добавьте в PATH.")

EDGE_LIMIT = 3000
PREVIEW_LEN = 300
VOICE_DEFAULT = "en-US-JennyNeural"

MAX_EDGE_TTS_CHARS = 999999  # рабочий лимит с запасом

BEST_FEMALE = ['en-US-JennyNeural', 'en-US-AriaNeural', 'en-GB-LibbyNeural']
BEST_MALE = ['en-US-GuyNeural', 'en-GB-RyanNeural']

@st.cache_data(show_spinner=False)
def get_english_and_russian_voices():
    try:
        voices = asyncio.run(edge_tts.list_voices())
        en_voices = [v for v in voices if v.get('Locale', '').startswith('en-')]
        ru_voices = [v for v in voices if v.get('Locale', '').startswith('ru-')]
        best_female = [v for v in en_voices if v['ShortName'] in BEST_FEMALE]
        best_male = [v for v in en_voices if v['ShortName'] in BEST_MALE]
        rest_female = sorted([v for v in en_voices if v.get('Gender') == 'Female' and v not in best_female], key=lambda v: v.get('FriendlyName') or v['ShortName'])
        rest_male = sorted([v for v in en_voices if v.get('Gender') == 'Male' and v not in best_male], key=lambda v: v.get('FriendlyName') or v['ShortName'])
        ru_female = sorted([v for v in ru_voices if v.get('Gender') == 'Female'], key=lambda v: v.get('FriendlyName') or v['ShortName'])
        ru_male = sorted([v for v in ru_voices if v.get('Gender') == 'Male'], key=lambda v: v.get('FriendlyName') or v['ShortName'])
        return best_female, rest_female, best_male, rest_male, ru_female, ru_male
    except Exception as e:
        st.warning(f"Не удалось получить список голосов Edge TTS: {e}")
        return (
            [{'ShortName': 'en-US-JennyNeural', 'FriendlyName': 'en-US-JennyNeural', 'Gender': 'Female', 'Locale': 'en-US'}],
            [],
            [{'ShortName': 'en-US-GuyNeural', 'FriendlyName': 'en-US-GuyNeural', 'Gender': 'Male', 'Locale': 'en-US'}],
            [],
            [{'ShortName': 'ru-RU-SvetlanaNeural', 'FriendlyName': 'ru-RU-SvetlanaNeural', 'Gender': 'Female', 'Locale': 'ru-RU'}],
            [{'ShortName': 'ru-RU-DmitryNeural', 'FriendlyName': 'ru-RU-DmitryNeural', 'Gender': 'Male', 'Locale': 'ru-RU'}]
        )

def group_voices_with_dividers_and_russian(best_female, rest_female, best_male, rest_male, ru_female, ru_male):
    grouped = []
    # Женские
    if best_female or rest_female:
        grouped.append(('—— Женские ——', None))
        grouped += [(v.get('FriendlyName', v['ShortName']), v['ShortName']) for v in best_female]
        grouped += [(v.get('FriendlyName', v['ShortName']), v['ShortName']) for v in rest_female]
    # Мужские
    if best_male or rest_male:
        grouped.append(('—— Мужские ——', None))
        grouped += [(v.get('FriendlyName', v['ShortName']), v['ShortName']) for v in best_male]
        grouped += [(v.get('FriendlyName', v['ShortName']), v['ShortName']) for v in rest_male]
    # Русские
    if ru_female or ru_male:
        grouped.append(('—— Русские голоса ——', None))
        if ru_female:
            grouped.append(('— Женские (RU) —', None))
            grouped += [(v.get('FriendlyName', v['ShortName']), v['ShortName']) for v in ru_female]
        if ru_male:
            grouped.append(('— Мужские (RU) —', None))
            grouped += [(v.get('FriendlyName', v['ShortName']), v['ShortName']) for v in ru_male]
    return grouped

def split_text(text, limit=EDGE_LIMIT):
    parts = []
    while len(text) > limit:
        split_idx = text.rfind('\n', 0, limit)
        if split_idx == -1 or split_idx < limit // 2:
            split_idx = limit
        parts.append(text[:split_idx])
        text = text[split_idx:]
    if text.strip():
        parts.append(text)
    return parts

def get_temp_mp3():
    return os.path.join(tempfile.gettempdir(), f"edge_tts_{uuid.uuid4().hex}.mp3")

def format_rate_volume(val):
    return f"{val:+d}%"

async def tts_to_mp3(text, voice, rate, volume, out_path):
    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=format_rate_volume(rate),
        volume=format_rate_volume(volume)
    )
    await communicate.save(out_path)

# --- UI ---
st.set_page_config(page_title="Нейро-Голос", layout="centered")
st.title("Генерация английской и русской озвучки через Microsoft Edge TTS")

st.markdown("""
**Введите текст для озвучки:**
""")
text = st.text_area("Текст для озвучки", height=200, key="input_text")

# Лимит символов
if len(text) > MAX_EDGE_TTS_CHARS:
    st.warning(f"Текст превышает лимит {MAX_EDGE_TTS_CHARS} символов и будет обрезан!")
    text = text[:MAX_EDGE_TTS_CHARS]

best_female, rest_female, best_male, rest_male, ru_female, ru_male = get_english_and_russian_voices()
grouped_options = group_voices_with_dividers_and_russian(best_female, rest_female, best_male, rest_male, ru_female, ru_male)
labels = [opt[0] for opt in grouped_options]
shortnames = [opt[1] for opt in grouped_options]
real_indices = [i for i, s in enumerate(shortnames) if s is not None]

if 'selected_voice' not in st.session_state:
    st.session_state.selected_voice = VOICE_DEFAULT

col1, col2 = st.columns(2)
with col1:
    # Индекс по сохранённому голосу среди всех (с учётом разделителей)
    if st.session_state.selected_voice in shortnames:
        default_idx = shortnames.index(st.session_state.selected_voice)
    else:
        default_idx = real_indices[0] if real_indices else 0
    selected_idx = st.selectbox("Голос:", range(len(labels)), format_func=lambda i: labels[i], index=default_idx)
    # Если выбран разделитель — не меняем голос
    if shortnames[selected_idx] is not None:
        st.session_state.selected_voice = shortnames[selected_idx]
    voice = st.session_state.selected_voice
with col2:
    # Описание выбранного голоса
    vinfo = next((v for v in best_female + rest_female + best_male + rest_male + ru_female + ru_male if v['ShortName'] == voice), None)
    if vinfo:
        st.markdown(f"**Выбранный голос:** `{voice}`  ")
        st.markdown(f"*{vinfo.get('FriendlyName', voice)}*  ")
        st.markdown(f"**Регион:** `{vinfo.get('Locale','')}`  |  **Пол:** `{vinfo.get('Gender','')}`")
    else:
        st.markdown(f"**Выбранный голос:** `{voice}`")

rate = st.slider("Скорость (Rate, %)", -50, 50, 0, 1)
volume = st.slider("Громкость (Volume, %)", -50, 50, 0, 1)

col3, col4 = st.columns(2)
preview_clicked = col3.button("🔊 Preview (первые 300 символов)")
generate_clicked = col4.button("🎵 Generate WAV (весь текст)")

status = st.empty()

if preview_clicked and text.strip():
    preview_text = text[:PREVIEW_LEN]
    status.info("Генерируется предпрослушка...")
    try:
        mp3_path = get_temp_mp3()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tts_to_mp3(preview_text, voice, rate, volume, mp3_path))
        audio = AudioSegment.from_file(mp3_path, format="mp3")
        wav_bytes = audio.export(format="wav").read()
        
        # Создаем колонки для предпрослушки
        col_preview_download, col_preview_play = st.columns(2)
        
        with col_preview_download:
            st.download_button("⬇️ Скачать предпрослушку", wav_bytes, file_name="preview.wav", mime="audio/wav")
        
        with col_preview_play:
            st.audio(wav_bytes, format="audio/wav", start_time=0)
        
        status.success("Предпрослушка готова!")
        os.remove(mp3_path)
    except Exception as e:
        status.error(f"Ошибка предпрослушки: {e}")

if generate_clicked and text.strip():
    status.info("Генерация озвучки...")
    parts = split_text(text)
    n_parts = len(parts)
    status.write(f"Текст разбит на {n_parts} сегмент(ов).")
    temp_mp3_files = []
    try:
        for i, part in enumerate(parts):
            status.write(f"Генерация сегмента {i+1}/{n_parts}...")
            mp3_path = get_temp_mp3()
            temp_mp3_files.append(mp3_path)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(tts_to_mp3(part, voice, rate, volume, mp3_path))
        # Объединяем все mp3 в один wav
        status.write("Объединение сегментов...")
        combined = AudioSegment.empty()
        for fname in temp_mp3_files:
            combined += AudioSegment.from_file(fname, format="mp3")
        out_path = os.path.join(os.getcwd(), "output.wav")
        combined.export(out_path, format="wav")
        for fname in temp_mp3_files:
            os.remove(fname)
        status.success(f"Готово! Итоговый файл: {out_path}")
        st.markdown(f"**Путь к файлу:** `{out_path}`")
        st.markdown(f"**Голос:** `{voice}`  |  **Сегментов:** {n_parts}")
        
        # Создаем колонки для кнопок скачивания и прослушивания
        col_download, col_play = st.columns(2)
        
        with col_download:
            with open(out_path, "rb") as f:
                st.download_button("⬇️ Скачать output.wav", f, file_name="output.wav", mime="audio/wav")
        
        with col_play:
            # Добавляем аудиоплеер для прослушивания в браузере
            with open(out_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/wav", start_time=0)
    except Exception as e:
        status.error(f"Ошибка генерации: {e}")
    finally:
        for fname in temp_mp3_files:
            if os.path.exists(fname):
                os.remove(fname)
st.markdown("---", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 20px; background: #1e1e1e; border: 1px solid #333; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); font-family: 'Segoe UI', sans-serif;">
    <div style="font-size: 24px; color: white; font-weight: bold; margin-bottom: 6px;">
         Нейро-Голос
    </div>
    <div style="font-size: 15px; color: #999; margin-bottom: 12px;">
        Нейроново 2025
    </div>
    <a href="https://github.com/neuronovo-X/neurovoice" target="_blank" style="color: #facc15; font-weight: bold; text-decoration: none; font-size: 16px;">
        🌟 GitHub 🌟 
    </a>
</div>
""", unsafe_allow_html=True)

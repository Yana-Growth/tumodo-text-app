import streamlit as st
import os
import pandas as pd
import pypdf
import io
import time

# Try to import google-generativeai
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Set page config
st.set_page_config(page_title="Tumodo AI | Creative Generator", layout="wide", page_icon="🎨")

# --- Custom CSS (Same as Text Generator for consistency) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #000047; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    [data-testid="stSidebar"] { background-color: #141e28; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6 { color: #000047 !important; font-weight: 800; }
    .main p, .main li, .main span, .main div[class*="stMarkdown"] { color: #000047 !important; }
    label *, label { color: #000047 !important; font-weight: bold !important; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb='select'] {
        background-color: #F8F9FA !important; color: #000047 !important; border: none !important;
        border-radius: 20px !important; padding: 10px 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    .stButton > button {
        background-color: #247cff !important; color: white !important; border: none !important;
        border-radius: 20px !important; padding: 12px 24px; font-weight: 700; transition: all 0.2s;
        box-shadow: 0 4px 10px rgba(36, 124, 255, 0.3);
    }
    .stButton > button:hover { background-color: #1a60cc !important; box-shadow: 0 6px 14px rgba(36, 124, 255, 0.4); }
    .stSuccess { background-color: #d1e7dd; color: #000047 !important; border-radius: 20px !important; border: none !important; }
    .option-card { background-color: #F8F9FA; border-radius: 20px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
</style>
""", unsafe_allow_html=True)

# Knowledge Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GUIDEBOOK_PATH = os.path.join(BASE_DIR, "TRIVIO-guidebook (1).pdf")
EXAMPLES_PATH = os.path.join(BASE_DIR, "Тексты объявлений FB.pdf")
BRAND_POSITIONING_PATH = os.path.join(BASE_DIR, "Tumodo_Brand platform & positioning.pdf")

@st.cache_resource
def load_pdf_text(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error: {e}"

# --- Setup API Models ---
def get_text_model(api_key):
    genai.configure(api_key=api_key)
    try:
        return genai.GenerativeModel('gemini-2.5-flash')
    except:
        return genai.GenerativeModel('gemini-1.5-pro')

def generate_image_with_imagen(prompt, api_key, aspect_ratio="1:1"):
    import requests, io
    from PIL import Image
    import urllib.parse
    
    # Map visual aspect ratio to what pollinations/gemini understands
    width, height = 1024, 1024
    if aspect_ratio == "16:9":
        width, height = 1024, 576
    elif aspect_ratio == "9:16":
        width, height = 576, 1024
    elif aspect_ratio == "4:3":
        width, height = 1024, 768
        
    try:
        # Pushing the request to Pollinations but with lower resolution if it's timing out, and with no caching
        encoded_prompt = urllib.parse.quote(prompt + " high quality, b2b saas, ad")
        # Added a random seed to prevent caching issues and nologo
        import random
        seed = random.randint(1, 100000)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
        
        # We increase timeout and add a custom header
        headers = {'User-Agent': 'TumodoCreativeApp/1.0'}
        response = requests.get(url, headers=headers, timeout=45)
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Сбой генерации (Сервер перегружен). Попробуйте сгенерировать по одной идее за раз.")
            return None
    except Exception as e:
        st.error(f"Таймаут или ошибка сети: {e}. Попробуйте еще раз.")
        return None

# Sidebar
with st.sidebar:
    st.header("⚙️ Настройки и База знаний")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Требуется для генерации идей и картинок")
    st.divider()
    st.markdown("**Загружены документы:**")
    
    tov_text = load_pdf_text(GUIDEBOOK_PATH)
    examples_text = load_pdf_text(EXAMPLES_PATH)
    brand_text = load_pdf_text(BRAND_POSITIONING_PATH)
    
    if tov_text: st.success("✅ Гайдбук")
    
    if examples_text: st.success("✅ Примеры FB")
    else: st.error("❌ Примеры FB")
    
    if brand_text: st.success("✅ Бренд позиционирование")
    else: st.error("❌ Бренд позиционирование")

st.title("🎨 Аналитика и Генератор Креативов")
st.markdown("Загрузите статистику текущих креативов (Excel/CSV), референсы визуалов, и получите 8-10 новых рабочих идей на основе брендбука.")

# --- Step 1: Uploads ---
st.subheader("1. Загрузка данных")
col_stats, col_vis = st.columns(2)

with col_stats:
    stats_file = st.file_uploader("📊 Загрузить статистику (Excel / CSV)", type=['xlsx', 'csv'])
    stats_data = None
    if stats_file:
        try:
            if stats_file.name.endswith('.csv'):
                try:
                    stats_data = pd.read_csv(stats_file, sep=None, engine='python')
                except Exception:
                    stats_file.seek(0)
                    stats_data = pd.read_csv(stats_file, sep=';', encoding='utf-8')
            else:
                stats_data = pd.read_excel(stats_file)
            st.success(f"Загружено строк: {len(stats_data)}")
            with st.expander("Посмотреть данные"):
                st.dataframe(stats_data.head())
        except Exception as e:
            st.error(f"Ошибка чтения файла: {e}")

with col_vis:
    visual_files = st.file_uploader("🖼️ Загрузить текущие визуалы (опционально)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    # Determine target aspect ratio based on the FIRST uploaded image
    target_aspect_ratio = "1:1" # default
    
    if visual_files:
        st.success(f"Загружено визуалов: {len(visual_files)}")
        # Show thumbnails
        cols = st.columns(4)
        for i, f in enumerate(visual_files):
            from PIL import Image
            img = Image.open(f)
            # If it's the first image, calculate the aspect ratio
            if i == 0:
                w, h = img.size
                ratio = w / h
                if ratio > 1.2:
                    target_aspect_ratio = "16:9"
                elif ratio < 0.8:
                    target_aspect_ratio = "9:16"
                elif ratio > 1.05:
                    target_aspect_ratio = "4:3"
                else:
                    target_aspect_ratio = "1:1"
                st.session_state.target_aspect_ratio = target_aspect_ratio
                st.caption(f"📐 Определен формат: {target_aspect_ratio}")
                
            cols[i % 4].image(img, use_container_width=True)

st.divider()

# --- Step 2: Generation Setup ---
st.subheader("2. Платформа и Настройки")
c1, c2 = st.columns(2)
with c1:
    geo = st.selectbox("Целевая страна (ГЕО)", ["Индия", "ОАЭ", "Саудовская Аравия", "Казахстан", "Германия", "Глобальный рынок"])
with c2:
    platform = st.selectbox("Для какой платформы генерируем?", ["Meta (Facebook/Instagram)", "LinkedIn"])

additional_focus = st.text_area("Дополнительные пожелания / Фокус (Опционально)", placeholder="Например: Сфокусироваться на тех, у кого хорошо работает CTR, или сделать упор на экономию времени...")

api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")

if "ideas" not in st.session_state:
    st.session_state.ideas = []

generate_ideas_btn = st.button("💡 Сгенерировать 8-10 идей для креативов", type="primary", use_container_width=True)

if generate_ideas_btn:
    if not HAS_GENAI:
        st.error("Библиотека google-generativeai не установлена.")
    elif not api_key:
        st.error("Введите API ключ в боковом меню.")
    elif stats_data is None:
        st.error("Пожалуйста, загрузите файл со статистикой.")
    else:
        try:
            model = get_text_model(api_key)
            
            # Prepare data string
            stats_string = stats_data.to_string(index=False)
            # Shorten if too large (e.g. max 5000 chars)
            if len(stats_string) > 5000:
                stats_string = stats_string[:5000] + "\n... (данные усечены)"
                
            prompt = f"""
            Ты - senior Art Director и Performance Marketer в Tumodo (B2B SaaS для бизнес-тревела).
            
            Твоя задача — проанализировать статистику по запущенным рекламным креативам и предложить 8-10 НОВЫХ, сильных и РАЗНООБРАЗНЫХ идей для создания новых визуалов (креативов, которые "пробьют баннерную слепоту").
            
            ЦЕЛЕВОЙ РЫНОК / ГЕО: {geo}
            ПЛАТФОРМА: {platform}
            ФОКУС: {additional_focus}
            
            СТАТИСТИКА ПО ТЕКУЩИМ КРЕАТИВАМ:
            {stats_string}
            
            БРЕНД КОНТЕКСТ:
            {str(brand_text)[:2000]}
            
            TONE OF VOICE & ПРИМЕРЫ:
            {str(tov_text)[:1000]}
            {str(examples_text)[:1000]}
            
            ТРЕБОВАНИЯ К ИДЕЯМ:
            - Идеи должны быть разнообразными: используй людей, интерфейсы приложения (mockups), метафоры, 3D элементы, реальные фото из B2B ситуаций. Не только абстракции!
            - Опирайся на лучшие практики B2B SaaS рекламы, адаптируя их под специфику рынка: {geo} (учитывай их культурный код и бизнес-подход).
            - Изображения будут генерироваться НЕЙРОСЕТЬЮ БЕЗ ТЕКСТА на фоне! Поэтому придумывай визуал так, чтобы он работал сам по себе.
            - Текстовый посыл (копирайт) будет накладываться поверх картинки дизайнером позже.
            
            ТРЕБОВАНИЯ К ФОРМАТУ ОТВЕТА (строго соблюдай структуру):
            Верни ровно 8-10 идей. Каждую идею разделяй СТРОГО строкой "====IDEA====". Ничего не пиши до первой идеи и после последней.
            В каждой идее опиши:
            1. Название/Концепцию
            2. Описание ВИЗУАЛА для генерации (очень подробно: объекты, люди, интерфейс, композиция, освещение, цвета). Укажи, что на самой картинке НЕТ текста.
            3. Рекомендуемый текст: 2-3 мощных варианта Headline и Primary Text, с какими формулировками этот визуал будет считываться лучше всего.
            4. Объяснение: почему это сработает на рынке ({geo}), опираясь на брендбук и статистику.
            """
            
            with st.spinner("Анализирую данные и генерирую идеи... Это может занять около минуты."):
                response = model.generate_content(prompt)
                raw_text = response.text
                
                ideas = [i.strip() for i in raw_text.split("====IDEA====") if i.strip()]
                st.session_state.ideas = ideas
                st.success(f"Сгенерировано {len(ideas)} идей!")
                
        except Exception as e:
            st.error(f"Ошибка при генерации: {e}")

# --- Step 3: Selection and Image Generation ---
if "ideas" in st.session_state and len(st.session_state.ideas) > 0:
    st.divider()
    st.subheader("3. Выберите идеи для генерации картинок")
    
    selected_ideas = []
    
    for i, idea_text in enumerate(st.session_state.ideas):
        st.markdown('<div class="option-card">', unsafe_allow_html=True)
        is_selected = st.checkbox(f"Выбрать Идею {i+1}", key=f"check_{i}")
        if is_selected:
            selected_ideas.append((i, idea_text))
            
        st.markdown(idea_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if len(selected_ideas) > 0:
        st.info(f"Выбрано идей: {len(selected_ideas)}")
        gen_img_btn = st.button("🖼️ Сгенерировать картинки для выбранных идей (Google Imagen)", type="primary")
        
        if gen_img_btn:
            for index, idea_content in selected_ideas:
                st.write(f"### Резульат для Идеи {index+1}")
                st.info("⌛ Отправка запроса в Google Imagen API... Генерация занимает около 10-15 секунд.")
                
                # We ask the text model to summarize the idea into a clean short English prompt for Imagen
                prompt_maker = get_text_model(api_key)
                prompt_for_imagen = f"Extract only the pure visual description from this idea and translate it into a highly detailed English image generation prompt (max 300 chars) for an ad creative. Important: You must specify that the image should contain NO text, NO letters, and NO words:\n\n{idea_content}"
                
                try:
                    summary_result = prompt_maker.generate_content(prompt_for_imagen)
                    english_prompt = summary_result.text.strip()
                    st.caption(f"**Промпт для нейросети:** {english_prompt}")
                    
                    # Fetch aspect ratio if we saved it from uploaded visuals
                    ratio_to_use = st.session_state.get('target_aspect_ratio', "1:1")
                    image = generate_image_with_imagen(english_prompt, api_key, aspect_ratio=ratio_to_use)
                    
                    if image:
                        st.image(image, caption=f"Визуал для идеи {index+1} (Формат: {ratio_to_use})", use_container_width=True)
                        
                        # Add download button
                        buf = io.BytesIO()
                        image.save(buf, format="JPEG")
                        byte_im = buf.getvalue()
                        st.download_button(
                            label="📥 Скачать картинку",
                            data=byte_im,
                            file_name=f"tumodo_creative_idea_{index+1}.jpg",
                            mime="image/jpeg",
                            key=f"dl_{index}"
                        )
                except Exception as e:
                    st.error(f"Ошибка при обработке Идеи {index+1}: {e}")
                

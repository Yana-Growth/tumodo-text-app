import streamlit as st
import os
import pypdf

# Try to import google-generativeai
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Set page config with custom title
st.set_page_config(page_title="Tumodo AI | Ad Generator", layout="wide", page_icon="🚀")

# --- Custom CSS for Light Theme & Blue Accents ---
st.markdown("""
<style>
    /* --- Global Settings --- */
    .stApp {
        background-color: #ffffff; /* pure white */
        color: #000047; /* dark blue text */
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #141e28;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #ffffff !important; /* White text on sidebar */
    }
    
    /* --- Headers --- */
    h1, h2, h3, h4, h5, h6 {
        color: #000047 !important;
        font-weight: 800;
    }
    
    /* --- General Text & Labels (Main Content) --- */
    .main p, .main li, .main span, .main label, .main div[class*="stMarkdown"] {
        color: #000047 !important;
    }
    
    /* Fix for Selectbox/Radio labels to ensure they are dark on white */
    .stSelectbox label, .stTextArea label, .stRadio label, .stTextInput label {
        color: #000047 !important;
        font-weight: 700;
        font-size: 1rem;
    }
    
    /* Radio options specifically */
    .stRadio div[role='radiogroup'] label div[data-testid='stMarkdownContainer'] p {
        color: #000047 !important;
    }
    
    /* --- Inputs (Fields) - No Borders, Shadow, 20px Radius --- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb='select'] {
        background-color: #F8F9FA !important; /* Very Pale Gray */
        color: #000047 !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 10px 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); /* Soft shadow instead of border */
    }
    
    /* Focus State - Soft Blue Glow */
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb='select']:focus-within {
        box-shadow: 0 0 0 3px rgba(36, 124, 255, 0.2) !important; /* Soft blue glow */
        background-color: #ffffff !important;
    }
    
    /* --- Buttons --- */
    .stButton > button {
        background-color: #247cff !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 12px 24px;
        font-weight: 700;
        transition: all 0.2s;
        box-shadow: 0 4px 10px rgba(36, 124, 255, 0.3);
    }
    .stButton > button:hover {
        background-color: #1a60cc !important;
        box-shadow: 0 6px 14px rgba(36, 124, 255, 0.4);
    }
    
    /* Secondary Button style for individual regeneration */
    button[kind="secondary"] {
        background-color: #F8F9FA !important;
        color: #247cff !important;
        border: 1px solid #247cff !important;
        box-shadow: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: #e2e8f0 !important;
        color: #1a60cc !important;
    }

    /* --- Success/Info Boxes --- */
    .stSuccess {
        background-color: #d1e7dd;
        color: #000047 !important;
        border-radius: 20px !important;
        border: none !important;
    }
    
    /* --- Captions --- */
    .stCaption {
        color: #000047 !important;
        opacity: 0.7;
    }
    
    /* Remove top padding specifically for clean look */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Cards for options */
    .option-card {
        background-color: #F8F9FA;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# Paths to Knowledge Base files (Use simple ASCII names for GitHub/Linux deploy)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GUIDEBOOK_PATH = os.path.join(BASE_DIR, "guidebook.pdf")
EXAMPLES_PATH = os.path.join(BASE_DIR, "examples.pdf")
BRAND_POSITIONING_PATH = os.path.join(BASE_DIR, "brand.pdf")
GERMAY_PRESENTATION_PATH = os.path.join(BASE_DIR, "germany.pdf")

@st.cache_resource
def load_pdf_text(file_path):
    """Extracts text from a PDF file."""
    if not os.path.exists(file_path):
        return None
    try:
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- Session State Initialization ---
if "options" not in st.session_state:
    st.session_state.options = []
if "last_context" not in st.session_state:
    st.session_state.last_context = {}

st.title("🚀 Tumodo AI: Генератор рекламных текстов")
st.markdown("Сервис для создания эффективных объявлений с учетом Tone of Voice, позиционирования и маркетинговых фреймворков.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Настройки")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Введите ваш ключ API")
    
    st.divider()
    
    st.subheader("📚 База знаний")
    guidebook_text = load_pdf_text(GUIDEBOOK_PATH)
    if guidebook_text:
        st.success(f"✅ Гайдбук")
    else:
        st.error("❌ Гайдбук")
        
    examples_text = load_pdf_text(EXAMPLES_PATH)
    if examples_text:
        st.success(f"✅ Примеры")
    else:
        st.error("❌ Примеры")
        
    brand_text = load_pdf_text(BRAND_POSITIONING_PATH)
    if brand_text:
        st.success(f"✅ Бренд-платформа")
    else:
        st.error("❌ Бренд-платформа")
        
    germany_text = load_pdf_text(GERMAY_PRESENTATION_PATH)
    if germany_text:
        st.success(f"✅ Германия (Презентация)")
    else:
        st.error("❌ Германия")

# Helper to get the model
def get_model(api_key):
    genai.configure(api_key=api_key)
    try:
        return genai.GenerativeModel('gemini-3-flash-preview')
    except:
        return genai.GenerativeModel('gemini-3-pro-preview')

# --- Main Interface ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Вводные данные")
    main_message = st.text_area("Общий комментарий / Запрос:", height=120, placeholder="Например: 'Нам нужно достучаться до финансовых менеджеров в IT-сфере' или 'Сделай акцент на тотальной прозрачности'.")
    
    # Platform Selection with 2026 Context
    platform_options = {
        "Meta (Facebook/Instagram)": "Акцент на визуал, эмоции, короткие емкие тексты. Лимит заголовка ~40 симв.",
        "LinkedIn": "Профессиональный тон, B2B фокус. Лонгриды приветствуются.",
        "Google Ads (Search)": "Строгие лимиты: Заголовок 30 симв, Описание 90 симв. Подбирай ключи.",
        "Яндекс.Директ": "Заголовок 56 симв, Текст 81 симв. Обязательны уточнения.",
        "Яндекс.Бизнес": "Аудитория малого бизнеса. Простой и понятный язык."
    }
    platform = st.selectbox("Платформа", list(platform_options.keys()))
    st.caption(f"ℹ️ {platform_options[platform]}")
    
    # Marketing Frameworks
    framework = st.selectbox("Маркетинговый фреймворк", [
        "Без фреймворка (Свободный оптимизированный стиль)",
        "AIDA (Внимание, Интерес, Желание, Действие)",
        "PAS (Проблема, Усиление, Решение)",
        "JTBD (Jobs To Be Done)",
        "Метод скользкой горки (Шугерман)"
    ])
    
with col2:
    st.subheader("2. Параметры")
    
    c1, c2 = st.columns(2)
    with c1:
        language = st.selectbox("Язык", ["Русский", "Английский", "Немецкий", "Арабский", "Хинди", "Казахский"])
    with c2:
        geo = st.selectbox("ГЕО", ["Россия", "США", "ОАЭ", "Саудовская Аравия", "Индия", "Казахстан", "Германия", "Весь мир"])
        
    text_type = st.radio("Что генерируем?", ["Основной текст", "Заголовки", "Текст для визуала"], horizontal=True)

    st.divider()
    generate_btn = st.button("✨ Сгенерировать варианты", type="primary", use_container_width=True)

# --- Initial Generation Logic ---
api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")

if generate_btn:
    if not HAS_GENAI:
        st.error("Библиотека `google-generativeai` не установлена.")
    elif not api_key:
        st.error("Введите API ключ.")
    else:
        try:
            model = get_model(api_key)
            
            # Context construction
            tov_context = guidebook_text if guidebook_text else ""
            brand_context = brand_text if brand_text else ""
            examples_context = examples_text if examples_text else ""
            germany_context = germany_text if (germany_text and geo == "Германия") else ""
            
            # Save context for regenerations
            st.session_state.last_context = {
                "platform": platform,
                "language": language,
                "geo": geo,
                "framework": framework,
                "text_type": text_type,
                "message": main_message,
                "tov": tov_context[:3000],
                "brand": brand_context[:3000],
                "examples": examples_context[:2000],
                "germany": germany_context[:3000]
            }
            
            prompt = f"""
            Ты - крутой сеньор B2B копирайтер бренда Tumodo.
            
            ЗАДАЧА: Напиши ровно 4 варианта для платформы: {platform}.
            ТЕБЕ НУЖНО СГЕНЕРИРОВАТЬ ТОЛЬКО ЭТОТ ТИП ТЕКСТА: **{text_type}**
            
            - Если выбрано "Основной текст": пиши готовый текст для поста/рекламы (с абзацами, эмодзи, CTA).
            - Если выбрано "Заголовки": пиши только мощный, короткий, цепляющий заголовок.
            - Если выбрано "Текст для визуала": пиши только 1-2 короткие фразы, которые дизайнер крупно напишет на баннере.
            
            Раздели варианты СТРОГО строкой "====SEPARATOR====". Обязательно выведи ровно 4 текста без лишних вступлений.
            
            ПАРАМЕТРЫ:
            Язык: {language}. Регион/Страна: {geo}. Фреймворк: {framework} (используй логику фреймворка, но НЕ пиши слова "Attention:", "Interest:" и т.д. в самом тексте!).
            
            ЗАПРОС / КОММЕНТАРИЙ ОТ ПОЛЬЗОВАТЕЛЯ: "{main_message}"
            --- ПРАВИЛО ЗАПРОСА ---
            Обязательно учитывай комментарий пользователя. Если он просит сделать акцент на финдирах - делай. Если поле пустое, сам подбери лучшие триггеры для {geo} и {platform}.
            
            МЕГА ВАЖНЫЕ ПРАВИЛА ФОРМАТИРОВАНИЯ И СТИЛЯ:
            1. ВАЖНО: Если ты используешь фреймворк (AIDA/PAS и тд), НИ В КОЕМ СЛУЧАЕ НЕ ПИШИ технические названия шагов типа "Attention:", "Interest:", "Проблема:", "Решение:". Текст должен быть слитным и органичным рекламным объявлением, а не сухой схемой!
            2. Объемы текста должны идеально подходить под выбранную платформу ({platform}), с правильным делением на абзацы и эмодзи. Не делай текст обрубком — он должен быть оптимальным для публикации.
            3. КАТЕГОРИЧЕСКИ запрещены шаблонные и пустые слова в любом языке: "unique", "уникальный", "best", "лучший", "индивидуальный подход", "революционный", "innovative". Вместо них используй только конкретные факты, цифры и выгоды (например, "экономия до 30%", "за 2 клика"). Пиши бодро и по делу.
            
            ОСОБЕННОСТИ 4-ГО ВАРИАНТА (БОНУС):
            Вариант 4 должен быть "Best Market Fit (SEO/Growth)" — сделай этот {text_type} максимально нестандартным и агрессивным для пробития баннерной слепоты в {geo}. Кратко обоснуй перед текстом в скобках, почему он сработает.
            
            КОНТЕКСТ ДЛЯ ИЗУЧЕНИЯ:
            Brand Positioning: {brand_context[:2000]}
            Tone of Voice: {tov_context[:2000]}
            Germany Specific Info: {germany_context[:2000]}
            
            ВАЖНО:
            1. Для Meta/LinkedIn делай {text_type} оптимального размера.
            2. Дели 4 варианта строками "====SEPARATOR====". Ничего не пиши до первого варианта и после последнего.
            """
            
            with st.spinner("🤖 Изучаю бренд-платформу и генерирую..."):
                response = model.generate_content(prompt)
                raw_text = response.text
                
                # Parse options
                options = [opt.strip() for opt in raw_text.split("====SEPARATOR====") if opt.strip()]
                
                # Make sure we have 4 options (fallback if model format fails)
                if len(options) == 0:
                    options = [raw_text]
                
                st.session_state.options = options
                
        except Exception as e:
            st.error(f"Критическая ошибка: {e}")

# --- Display Results & Feedback Loop ---
if st.session_state.options:
    st.divider()
    st.subheader("📢 Результаты (нажмите на варианты для редактирования)")
    
    for i, opt_text in enumerate(st.session_state.options):
        # UI Card for option
        st.markdown('<div class="option-card">', unsafe_allow_html=True)
        
        col_text, col_feedback = st.columns([1.5, 1])
        
        with col_text:
            title = "Вариант 4 (Best SEO & Market Fit 🌟)" if i == 3 and len(st.session_state.options) == 4 else f"Вариант {i+1}"
            st.markdown(f"**{title}**")
            st.markdown(opt_text)
            
        with col_feedback:
            # Feedback form specific to this option
            feedback_key = f"fb_{i}"
            feedback = st.text_input(f"💭 Комментарий к Варианту {i+1}", key=feedback_key, placeholder="Например: 'Сделай агрессивнее' или 'Убери эмодзи'")
            
            # Use secondary styled button for regeneration
            if st.button(f"🔄 Пересгенерировать вариант {i+1}", key=f"btn_{i}", type="secondary"):
                if not api_key:
                    st.error("Нужен API ключ.")
                else:
                    try:
                        model = get_model(api_key)
                        ctx = st.session_state.last_context
                        regen_prompt = f"""
                        Ты редактируешь один из 4 вариантов рекламы Tumodo для платформы {ctx['platform']}.
                        Вот текущий текст:
                        {opt_text}
                        
                        ПОЛЬЗОВАТЕЛЬ ПОПРОСИЛ ВНЕСТИ ПРАВКУ В ЭТОТ ВАРИАНТ:
                        "{feedback}"
                        
                        Перепиши этот текст СТРОГО с учетом правки. 
                        Сохраняй язык ({ctx['language']}) и TOV бренда Tumodo.
                        Верни только новый готовый текст без лишних вступлений.
                        """
                        with st.spinner("Переписываю..."):
                            regen_response = model.generate_content(regen_prompt)
                            st.session_state.options[i] = regen_response.text
                            st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {e}")
                        
        st.markdown('</div>', unsafe_allow_html=True)

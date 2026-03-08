import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import io

# === КОНФИГУРАЦИЯ СТРАНИЦЫ ===
st.set_page_config(
    page_title="Julli Map Generator",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === СТИЛИ ===
st.markdown("""
<style>
    .main {
        background-color: #0D1117;
        color: #E6EDF3;
    }
    .sidebar .sidebar-content {
        background-color: #161B22;
    }
    h1, h2, h3 {
        color: #58A6FF;
    }
    p {
        color: #E6EDF3;
    }
</style>
""", unsafe_allow_html=True)

# === ЗАГОЛОВОК ===
st.markdown("""
<h1 style='text-align: center; color: #58A6FF;'>🗺 ПОВЕДЕНЧЕСКАЯ КАРТА JULLI</h1>
<h3 style='text-align: center; color: #D29922;'>Генератор еженедельных карт торговли</h3>
""", unsafe_allow_html=True)

st.markdown("---")

# === БОКОВАЯ ПАНЕЛЬ ===
st.sidebar.markdown("## ⚙️ ПАРАМЕТРЫ НЕДЕЛИ")

week_num = st.sidebar.number_input(
    "Номер недели (1-52):",
    value=12,
    min_value=1,
    max_value=52,
    step=1
)

date_range = st.sidebar.text_input(
    "Дата (формат: 17–21 фев 2026):",
    value="17–21 фев 2026"
)

total_result = st.sidebar.number_input(
    "Итоговый результат недели (%):",
    value=4.7,
    format="%.2f",
    step=0.1
)

# === ВКЛАДКИ ===
tab1, tab2, tab3, tab4 = st.tabs(["📊 Таблица данных", "🎨 Предпросмотр", "📝 Текст интерпретации", "📥 Скачивание"])

# === ПЕРЕМЕННЫЕ ===
days = ["Пн", "Вт", "Ср", "Чт", "Пт"]
hours = [f"{h:02d}:00" for h in range(24)]

# === ЦВЕТА ===
COLOR_BG = '#0D1117'
COLOR_STRONG_GREEN = '#3FB950'
COLOR_MOD_GREEN = '#238636'
COLOR_NEUTRAL = '#30363D'
COLOR_ORANGE = '#D29922'
COLOR_RED = '#F85149'
COLOR_SKIP = '#161B22'
COLOR_TEXT = '#E6EDF3'
COLOR_ACCENT = '#58A6FF'

# ============================================
# TAB 1 — ТАБЛИЦА ВВОДА ДАННЫХ
# ============================================
with tab1:
    st.subheader("Введите результаты торговли по часам")
    
    # Инициализируем сессию
    if 'data_values' not in st.session_state:
        st.session_state.data_values = {}
    if 'lot_values' not in st.session_state:
        st.session_state.lot_values = {}
    
    data = {}
    lots = {}
    
    st.markdown("### Результаты сделок (%)")
    st.info("💡 Совет: Вставьте данные из MT5 или Myfxbook. Пропуски = 0.")
    
    # Таблица результатов
    cols_header = st.columns([1, 1.5, 1.5, 1.5, 1.5, 1.5])
    with cols_header[0]:
        st.markdown("Час")
    for d_idx, day in enumerate(days):
        with cols_header[d_idx + 1]:
            st.markdown(f"{day}")
    
    for h_idx, hour in enumerate(hours):
        cols = st.columns([1, 1.5, 1.5, 1.5, 1.5, 1.5])
        
        with cols[0]:
            st.markdown(f"{hour}")
        
        for d_idx in range(5):
            with cols[d_idx + 1]:
                key_data = f"data_{h_idx}_{d_idx}"
                value = st.number_input(
                    label="Результат %",
                    value=0.0,
                    format="%.2f",
                    step=0.01,
                    key=key_data,
                    label_visibility="collapsed"
                )
                data[f"{h_idx}_{d_idx}"] = value
    
    st.markdown("---")
    
    st.markdown("### Размеры лотов по часам")
    st.info("💡 Совет: Введите средние размеры лотов для визуализации адаптивности.")
    
    cols_header_lot = st.columns([1, 1.5, 1.5, 1.5, 1.5, 1.5])
    with cols_header_lot[0]:
        st.markdown("Час")
    for d_idx, day in enumerate(days):
        with cols_header_lot[d_idx + 1]:
            st.markdown(f"{day}")
    
    for h_idx, hour in enumerate(hours):
        cols_lot = st.columns([1, 1.5, 1.5, 1.5, 1.5, 1.5])
        
        with cols_lot[0]:
            st.markdown(f"{hour}")
        
        for d_idx in range(5):
            with cols_lot[d_idx + 1]:
                key_lot = f"lot_{h_idx}_{d_idx}"
                lot_val = st.number_input(
                    label="Лот",
                    value=0.0,
                    format="%.3f",
                    step=0.01,
                    key=key_lot,
                    label_visibility="collapsed"
                )
                lots[f"{h_idx}_{d_idx}"] = lot_val

# ============================================
# TAB 2 — ГЕНЕРАЦИЯ И ПРЕДПРОСМОТР
# ============================================
with tab2:
    st.subheader("Предпросмотр поведенческой карты")
    
    if st.button("🔄 Сгенерировать карту", use_container_width=True):
        
        # Преобразуем в матрицы
        data_matrix = np.zeros((24, 5))
        lots_matrix = np.zeros((24, 5))
        
        for h_idx in range(24):
            for d_idx in range(5):
                key_d = f"{h_idx}_{d_idx}"
                data_matrix[h_idx, d_idx] = data.get(key_d, 0)
                lots_matrix[h_idx, d_idx] = lots.get(key_d, 0)
        
        # Функция цвета
        def get_cell_color(val):
            if val == 0:
                return COLOR_SKIP
            if val > 0.8:
                return COLOR_STRONG_GREEN
            elif val > 0.2:
                return COLOR_MOD_GREEN
            elif val > -0.2:
                return COLOR_NEUTRAL
            elif val > -0.8:
                return COLOR_ORANGE
            else:
                return COLOR_RED
        
        # Функция точек
        def get_dots(lot_val):
            if lot_val == 0:
                return ""
            elif lot_val < 0.05:
                return "●"
            elif lot_val < 0.08:
                return "●●"
            else:
                return "●●●"
        
        # Построение графика
        fig, ax = plt.subplots(figsize=(12, 22))
        fig.patch.set_facecolor(COLOR_BG)
        ax.set_facecolor(COLOR_BG)
        
        cell_w, cell_h = 1.0, 1.0
        
        # Ячейки
        for h in range(24):
            for d in range(5):
                val = data_matrix[h, d]
                color = get_cell_color(val)
                
                rect = patches.FancyBboxPatch(
                    (d, 23 - h), cell_w * 0.92, cell_h * 0.92,
                    boxstyle="round,pad=0.05",
                    facecolor=color,
                    edgecolor='#21262D',
                    linewidth=0.8
                )
                ax.add_patch(rect)
                
                # Результат
                if val != 0:
                    ax.text(
                        d + 0.5, 23 - h + 0.35,
                        f"{val:+.2f}%",
                        ha='center', va='center',
                        fontsize=7, color=COLOR_TEXT,
                        fontfamily='monospace', fontweight='bold'
                    )
                
                # Точки лота
                dots = get_dots(lots_matrix[h, d])
                if dots:
                    ax.text(
                        d + 0.5, 23 - h + 0.65,
                        dots,
                        ha='center', va='center',
                        fontsize=8, color='white', fontweight='bold'
                    )
        
        # Подписи часов
        for h in range(24):
            ax.text(
                -0.7, 23 - h + 0.5,
                hours[h],
                ha='center', va='center',
                fontsize=8, color=COLOR_TEXT,
                fontfamily='monospace', fontweight='bold'
            )
        
        # Подписи дней
        for d in range(5):
            ax.text(
                d + 0.5, 24.5,
                days[d],
                ha='center', va='center',
                fontsize=10, color=COLOR_ACCENT,
                fontweight='bold'
            )
        
        # Суммы по дням
        for d in range(5):
            day_sum = np.sum(data_matrix[:, d])
            color = COLOR_STRONG_GREEN if day_sum > 0 else COLOR_RED
            ax.text(
                d + 0.5, -0.8,
                f"Σ {day_sum:+.2f}%",
                ha='center', va='center',
                fontsize=8, color=color, fontweight='bold'
            )
        
        # Суммы по часам
        for h in range(24):
            hour_sum = np.sum(data_matrix[h, :])
            if hour_sum != 0:
                color = COLOR_STRONG_GREEN if hour_sum > 0 else COLOR_RED
                ax.text(
                    5.8, 23 - h + 0.5,
                    f"{hour_sum:+.2f}%",
                    ha='center', va='center',
                    fontsize=7, color=color, fontweight='bold'
                )
        
        # Заголовок
        ax.text(
            2.5, 25.8,
            "🗺 ПОВЕДЕНЧЕСКАЯ КАРТА JULLI",
            ha='center', va='center',
            fontsize=15, color=COLOR_ACCENT, fontweight='bold'
        )
        ax.text(
            2.5, 25.3,
            f"Неделя #{week_num} | {date_range}",
            ha='center', va='center',
            fontsize=10, color=COLOR_TEXT, alpha=0.8
        )
        ax.text(
            2.5, 24.95,
            "XAU/USD | MT5",
            ha='center', va='center',
            fontsize=9, color=COLOR_ORANGE, fontweight='bold'
        )
        
        # Итоговый результат
        result_color = COLOR_STRONG_GREEN if total_result > 0 else COLOR_RED
        ax.text(
            2.5, -1.5,
            f"📊 ИТОГО: {total_result:+.2f}%",
            ha='center', va='center',
            fontsize=11, color=result_color, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=COLOR_SKIP, alpha=0.5, pad=0.5)
        )
        
        # Легенда
        legend_y = -2.8
        legend_items = [
            (COLOR_STRONG_GREEN, "Сильный (>+0.8%)"),
            (COLOR_MOD_GREEN, "Умерен (+0.2...+0.8%)"),
            (COLOR_NEUTRAL, "Нейтр (±0.2%)"),
            (COLOR_ORANGE, "Слабый (-0.8...-0.2%)"),
            (COLOR_RED, "Убыток (<-0.8%)"),
        ]
        
        for i, (color, label) in enumerate(legend_items):
            x = (i % 3) * 1.8 - 0.5
            y = legend_y - (i // 3) * 0.6
            rect = patches.Rectangle(
                (x, y), 0.3, 0.25,
                facecolor=color, edgecolor='#21262D', linewidth=0.5
            )
            ax.add_patch(rect)
            ax.text(
                x + 0.45, y + 0.125,
                label, fontsize=7, color=COLOR_TEXT, va='center'
            )
        
        ax.text(
            2.5, legend_y - 1.3,
            "● мин. лот  ●● средний  ●●● макс. лот",
            ha='center', va='center',
            fontsize=7, color=COLOR_TEXT, alpha=0.6, fontfamily='monospace'
        )
        
        # Параметры графика
        ax.set_xlim(-1.3, 6.8)
        ax.set_ylim(legend_y - 1.8, 26.2)
        ax.axis('off')
        
        plt.tight_layout()
        
        # Сохраняем
        st.session_state.fig = fig
        st.session_state.generated = True
        
        st.success("✅ Карта сгенерирована!")
    
    # Показываем карту
    if 'generated' in st.session_state and st.session_state.generated:
        st.pyplot(st.session_state.fig, use_container_width=True)

# ============================================
# TAB 3 — ТЕКСТ ИНТЕРПРЕТАЦИИ
# ============================================
with tab3:
    st.subheader("Текстовый разбор недели")
    
    st.info("💡 Редактируйте текст под конкретные результаты вашей недели.")
    
    interpretation = st.text_area(
        "Интерпретация результатов:",
        value=f"""🗺 ПОВЕДЕНЧЕСКАЯ КАРТА JULLI | Неделя #{week_num}

📊 Результат недели: {total_result:+.2f}%
📈 Лучший день: [введите]
📉 Сложный день: [введите]
🎯 Всего сделок: [введите]
🚫 Пропущено часов: [введите] из 120

━━━━━━━━━━━━━━━━━━━━━━

⏰ ТОП-3 ЧАСА НЕДЕЛИ:

1. [Час] — [Название]
   Σ [+X.XX]% | [X]/5 дней | Лот: макс
   [Описание логики]

2. [Час] — [Название]
   Σ [+X.XX]% | [X]/5 дней | Лот: макс
   [Описание логики]

3. [Час] — [Название]
   Σ [+X.XX]% | [X]/5 дней | Лот: макс
   [Описание логики]

━━━━━━━━━━━━━━━━━━━━━━

🔴 КРАСНАЯ ЗОНА НЕДЕЛИ:

[Описание убыточной сделки и адаптации]

━━━━━━━━━━━━━━━━━━━━━━

💡 КЛЮЧЕВОЙ ПРИНЦИП:

[Главный вывод из карты]

📊 Myfxbook: [ссылка]
""",
        height=300,
        key="interpretation"
    )

# ============================================
# TAB 4 — СКАЧИВАНИЕ
# ============================================
with tab4:
    st.subheader("📥 Скачивание файлов")
    
    if 'fig' in st.session_state and st.session_state.generated:
        
        # PNG
        buf = io.BytesIO()
        st.session_state.fig.savefig(
            buf,
            format='png',
            dpi=200,
            facecolor=COLOR_BG,
            bbox_inches='tight'
        )
        buf.seek(0)
        
        st.download_button(
            label="📥 Скачать карту (PNG)",
            data=buf,
            file_name=f"julli_map_week{week_num}.png",
            mime="image/png",
            use_container_width=True
        )
        
        # TXT
        text_buf = interpretation.encode('utf-8')
        st.download_button(
            label="📄 Скачать текст (TXT)",
            data=text_buf,
            file_name=f"julli_text_week{week_num}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # CSV
        csv_data = []
        for h_idx, hour in enumerate(hours):
            for d_idx, day in enumerate(days):
                key = f"{h_idx}_{d_idx}"
                csv_data.append({
                    'Час': hour,
                    'День': day,
                    'Результат %': data.get(key, 0),
                    'Лот': lots.get(key, 0)
                })
        
        df = pd.DataFrame(csv_data)
        csv_buf = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📊 Скачать данные (CSV)",
            data=csv_buf,
            file_name=f"julli_data_week{week_num}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.success("✅ Все файлы готовы!")
        
    else:
        st.warning("⚠️ Сначала сгенерируйте карту на вкладке '🎨 Предпросмотр'")

# === ФУТЕР ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #58A6FF; font-size: 12px;'>
    <p>🗺 Truth Quant Lab | Julli Map Generator</p>
    <p style='color: #D29922;'>Генерация поведенческих карт торговли</p>
</div>
""", unsafe_allow_html=True)

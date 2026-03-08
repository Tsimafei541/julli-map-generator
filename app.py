st.session_state.fig = fig
        st.session_state.generated = True
        
        st.success("✅ Карта сгенерирована!")
    
    # Показываем карту если она есть
    if 'generated' in st.session_state and st.session_state.generated:
        st.pyplot(st.session_state.fig, use_container_width=True)

# ============================================
# TAB 3 — ТЕКСТОВАЯ ИНТЕРПРЕТАЦИЯ
# ============================================
with tab3:
    st.subheader("Текстовый разбор недели")
    
    st.info("💡 Это шаблон. Редактируйте под конкретные результаты вашей недели.")
    
    interpretation = st.text_area(
        "Интерпретация результатов:",
        value=f"""🗺 ПОВЕДЕНЧЕСКАЯ КАРТА JULLI | Неделя #{week_num}

📊 Результат недели: {total_result:+.2f}%
📈 Лучший день: [введите]
📉 Сложный день: [введите]
🎯 Всего сделок: [введите]
🚫 Пропущено часов: [введите] из 120 ([введите]%)

━━━━━━━━━━━━━━━━━━━━━━

⏰ ТОП-3 ЧАСА НЕДЕЛИ:

1. [Час] — [Название]
   Σ [+X.XX]% | [X]/5 дней | Лот: [макс/средний/минимальный]
   [Описание поведения толпы и логики Julli]

2. [Час] — [Название]
   Σ [+X.XX]% | [X]/5 дней | Лот: [макс/средний/минимальный]
   [Описание поведения толпы и логики Julli]

3. [Час] — [Название]
   Σ [+X.XX]% | [X]/5 дней | Лот: [макс/средний/минимальный]
   [Описание поведения толпы и логики Julli]

━━━━━━━━━━━━━━━━━━━━━━

🔴 КРАСНАЯ ЗОНА НЕДЕЛИ:

[Час и описание убыточной сделки]
[Почему это произошло]
[Как Julli адаптируется]

━━━━━━━━━━━━━━━━━━━━━━

🔬 НАБЛЮДЕНИЕ НЕДЕЛИ:

[Интересный паттерн, аномалия, адаптация]

━━━━━━━━━━━━━━━━━━━━━━

💡 КЛЮЧЕВОЙ ПРИНЦИП:

[Главный вывод из карты]

📊 Myfxbook: [вставьте ссылку]
""",
        height=400,
        key="interpretation"
    )

# ============================================
# TAB 4 — СКАЧИВАНИЕ
# ============================================
with tab4:
    st.subheader("📥 Скачивание файлов")
    
    if 'fig' in st.session_state and st.session_state.generated:
        # Кнопка скачивания PNG
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
        
        # Кнопка скачивания текста
        text_buf = interpretation.encode('utf-8')
        st.download_button(
            label="📄 Скачать текстовый разбор (TXT)",
            data=text_buf,
            file_name=f"julli_interpretation_week{week_num}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Кнопка скачивания данных (CSV)
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
        
        st.success("✅ Все файлы готовы к скачиванию!")
        
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

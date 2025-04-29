import streamlit as st
import random

def telegram_data():
    params = st.query_params
    return {
        'name': params.get("name", ["Anonymous"]),
        'id': params.get("id", ["None"])
    }

user_data = telegram_data()

def initialize_game():
    st.session_state.game = {
        'field': [[None for _ in range(5)] for _ in range(5)],
        'mines': set(),
        'opened': set(),
        'bet': 0,
        'multiplier': 1.0,
        'game_active': False,
        'first_move': True,
        'game_over': False,
        'mine_position': None,
        'revealed': False
    }

if 'balance' not in st.session_state:
    st.session_state.balance = 0
    st.session_state.show_topup = False

if 'game' not in st.session_state:
    initialize_game()

st.set_page_config(
    page_title="Star Mines",
    page_icon="💣",
    layout="centered"
)

# Мобильные стили
st.markdown("""
<style>
    /* Основные стили для мобильных */
    @media (max-width: 768px) {
        /* Фиксируем размер кнопок */
        .stButton>button {
            width: 100% !important;
            height: 100% !important;
            min-width: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Центрируем содержимое */
        .st-emotion-cache-1kyxreq {
            justify-content: center !important;
        }
        
        /* Уменьшаем отступы */
        .st-emotion-cache-1y4p8pa {
            padding: 0.5rem !important;
        }
    }
    
    /* Общие стили для ячеек */
    .cell-container {
        position: relative;
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

def topup_balance(amount):
    st.session_state.balance += amount
    st.session_state.show_topup = False
    st.rerun()

def start_game():
    if st.session_state.balance < st.session_state.game['bet']:
        st.error("Недостаточно средств!")
        return
    st.rerun()
    
    mines = set()
    while len(mines) < 12:
        mine = (random.randint(0,4), random.randint(0,4))
        mines.add(mine)
    
    st.session_state.game.update({
        'mines': mines,
        'opened': set(),
        'multiplier': 1.0,
        'game_active': True,
        'first_move': True,
        'game_over': False,
        'mine_position': None,
        'revealed': False
    })
    st.session_state.balance -= st.session_state.game['bet']

def open_cell(row, col):
    if st.session_state.game['first_move']:
        st.session_state.game['first_move'] = False
    
    if (row, col) in st.session_state.game['mines']:
        st.session_state.game['game_over'] = True
        st.session_state.game['mine_position'] = (row, col)
        reveal_all_cells()
    else:
        st.session_state.game['opened'].add((row, col))
        st.session_state.game['multiplier'] = round(st.session_state.game['multiplier'] * 1.2, 1)

def reveal_all_cells():
    st.session_state.game['revealed'] = True

def cash_out():
    win = int(st.session_state.game['bet'] * st.session_state.game['multiplier'])
    st.session_state.balance += win
    initialize_game()

def continue_after_mine():
    initialize_game()

# Интерфейс
st.markdown("<h1 style='text-align:center; font-size:1.5rem; margin:5px 0;'>🌟 Star Mines 💣</h1>", unsafe_allow_html=True)

# Блок баланса
with st.container():
    st.markdown(f"<div style='text-align:center; font-size:1.1rem; margin:5px 0;'>@{user_data['name']}</div>", unsafe_allow_html=True)
with st.container():
    st.markdown(f"<div style='text-align:center; font-size:1.1rem; margin:5px 0;'>💰 Баланс: {st.session_state.balance} ⭐️</div>", unsafe_allow_html=True)
    if st.button("➕ Пополнить", key="topup_btn", use_container_width=True):
        st.session_state.show_topup = not st.session_state.show_topup

# Форма пополнения
if st.session_state.show_topup:
    with st.form("topup_form"):
        amount = st.number_input("Сумма пополнения (⭐️)", min_value=10, step=5)
        cols = st.columns(2)
        with cols[0]:
            if st.form_submit_button("Пополнить"):
                topup_balance(amount)
        with cols[1]:
            if st.form_submit_button("Отмена"):
                st.session_state.show_topup = False
                st.rerun()
else:
    # Блок ставки и игры
    MIN_BET = 10
    if not st.session_state.game['game_active']:
        if st.session_state.balance >= MIN_BET:
            bet = st.number_input(
                "Ставка (⭐️)",
                min_value=MIN_BET,
                max_value=st.session_state.balance,
                step=5,
                key="bet_input"
            )
            st.session_state.game['bet'] = bet
            if st.button("🎮 Начать игру", type="primary", use_container_width=True):
                start_game()
        else:
            st.markdown("<div style='color:red; text-align:center;'>Минимальная ставка 10⭐️</div>", unsafe_allow_html=True)

    # Игровое поле
    if st.session_state.game['game_active']:
        st.markdown(f"<div style='text-align:center; font-size:1.2rem; margin:10px 0;'>🔥 Множитель: {st.session_state.game['multiplier']:.1f}x</div>", unsafe_allow_html=True)
        
        # Создаем минное поле 5x5
        for row in range(5):
            cols = st.columns(5)
            for col in range(5):
                with cols[col]:
                    pos = (row, col)
                    if pos in st.session_state.game['opened']:
                        st.markdown(
                            '<div class="cell-container" style="background-color:#88ff88;">💰</div>', 
                            unsafe_allow_html=True
                        )
                    elif st.session_state.game['revealed'] and pos in st.session_state.game['mines']:
                        emoji = "💣" if pos == st.session_state.game['mine_position'] else "💥"
                        bg_color = "#ff4444" if pos == st.session_state.game['mine_position'] else "#ffaaaa"
                        st.markdown(
                            f'<div class="cell-container" style="background-color:{bg_color};">{emoji}</div>', 
                            unsafe_allow_html=True
                        )
                    elif st.session_state.game['game_over'] or st.session_state.game['revealed']:
                        st.markdown(
                            '<div class="cell-container" style="background-color:#e0e0e0;">🟦</div>', 
                            unsafe_allow_html=True
                        )
                    else:
                        if st.button(
                            "🟦",
                            key=f"cell_{row}_{col}",
                            on_click=open_cell,
                            args=(row, col),
                            use_container_width=True
                        ):
                            pass

        # Управление игрой
        if st.session_state.game['game_over']:
            st.error("💣 Вы нашли мину!")
            st.button("🔄 Новая игра", type="primary", on_click=continue_after_mine, use_container_width=True)
        elif not st.session_state.game['first_move']:
            st.button("🏦 Забрать выигрыш", type="primary", on_click=cash_out, use_container_width=True)

# Правила игры
with st.expander("📖 Правила игры"):
    st.write("""
    1. Минимальная ставка: 10 ⭐️
    2. Открывайте клетки на поле 5x5
    3. Множитель растет на 20% за безопасную клетку
    4. Найдете мину - игра завершается
    5. Можно забрать выигрыш в любой момент
    """)
with st.expander("🔗 Реферальная программа"):
    st.write(f"""
    💬 Приглашай друзей по своей ссылке:\n
    https://t.me/AppYourSiteBot/?start=id{user_data['id']}\n\n
    ✅ И получай бонусы!\n
    """)

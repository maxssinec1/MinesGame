import streamlit as st
import random

def telegram_data():
    params = st.query_params
    return {
        'name': params.get("name", ["Anonymous"]),
        'id': params.get("id", ["None"])
    }

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

# Инициализация состояния
if 'balance' not in st.session_state:
    st.session_state.balance = 0
    st.session_state.show_topup = False  # Контроль отображения формы пополнения

if 'game' not in st.session_state:
    initialize_game()

st.set_page_config(
    page_title="Star Mines",
    page_icon="💣",
)

st.markdown("""
<style>
    /* Стили для кнопок игрового поля */
    .minefield-button>button {
        width: 60px !important;
        height: 60px !important;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        border-radius: 8px !important;
        border: 2px solid #4a4a4a !important;
        padding: 0 !important;
    }
    
    /* Стили для содержимого ячеек */
    .cell-content {
        width: 60px;
        height: 60px;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        border-radius: 8px;
        border: 2px solid #4a4a4a;
    }
    
    /* Стили для разных состояний ячеек */
    .mine-cell {
        background-color: #ffcccc !important;
    }
    .safe-cell {
        background-color: #ccffcc !important;
    }
    
    /* Общие стили */
    .big-font {
        font-size: 24px !important;
        text-align: center;
    }
    .game-over {
        color: red;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .balance-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .topup-form {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def topup_balance(amount):
    st.session_state.balance += amount
    st.session_state.show_topup = False
    st.rerun()

def start_game():
    if st.session_state.balance < st.session_state.game['bet']:
        st.error("Недостаточно средств для ставки!")
        return
    
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
    st.rerun()

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
    st.success(f"✅ Вы успешно забрали {win} ⭐️")
    initialize_game()
    st.rerun()

def continue_after_mine():
    initialize_game()
    st.rerun()

st.title("🌟 Star Mines 💣")

user_data = telegram_data()

with st.container():
    cols = st.columns([4, 1])
    with cols[0]:
        st.subheader(f"@{user_data["name"]}")

with st.container():
    cols = st.columns([4, 1])
    with cols[0]:
        st.subheader(f"💰 Текущий баланс: {st.session_state.balance} ⭐️", divider="rainbow")
    with cols[1]:
        if st.session_state.balance > 0 and not st.session_state.game['game_active']:
            if st.button("➕ Пополнить", key="topup_btn"):
                st.session_state.show_topup = True
                st.rerun()

# Форма пополнения баланса
if st.session_state.get('show_topup', False):
    with st.form("topup_form", clear_on_submit=True):
        st.markdown('<div class="topup-form">', unsafe_allow_html=True)
        amount = st.number_input(
            "Сумма пополнения (⭐️)",
            min_value=10,
            step=5,
            key="topup_amount"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Пополнить"):
                topup_balance(amount)
        with col2:
            if st.form_submit_button("Отмена"):
                st.session_state.show_topup = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Основная кнопка пополнения (только при нулевом балансе)
if st.session_state.balance == 0 and not st.session_state.game['game_active']:
    if st.button("➕ Пополнить баланс", key="initial_topup"):
        st.session_state.show_topup = True
        st.rerun()

# Блок ставки (только если баланс достаточен)
MIN_BET = 10
if st.session_state.balance >= MIN_BET and not st.session_state.game['game_active']:
    with st.expander("🛎️ Сделать ставку", expanded=True):
        bet = st.number_input(
            "Сумма ставки (⭐️)",
            min_value=MIN_BET,
            max_value=st.session_state.balance,
            step=5,
            key="bet_input"
        )
        st.session_state.game['bet'] = bet
        if st.button("🎮 Начать игру", key="start_game"):
            start_game()
elif st.session_state.balance < MIN_BET and st.session_state.balance > 0 and not st.session_state.game['game_active']:
    st.markdown('<p class="game-over">Недостаточно средств для минимальной ставки ( 10 ⭐️)</p>', unsafe_allow_html=True)

# Игровое поле
if st.session_state.game['game_active']:
    st.write(f"🔥 Текущий множитель: {st.session_state.game['multiplier']:.1f}x")
    
    # Контейнер для центрирования поля
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            for row in range(5):
                cols = st.columns(5, gap="small")
                for col in range(5):
                    with cols[col]:
                        if st.session_state.game['revealed']:
                            if (row, col) in st.session_state.game['mines']:
                                if (row, col) == st.session_state.game['mine_position']:
                                    st.markdown(
                                        '<div class="cell-content mine-cell">💣</div>', 
                                        unsafe_allow_html=True
                                    )
                                else:
                                    st.markdown(
                                        '<div class="cell-content mine-cell">💥</div>', 
                                        unsafe_allow_html=True
                                    )
                            elif (row, col) in st.session_state.game['opened']:
                                st.markdown(
                                    '<div class="cell-content safe-cell">💰</div>', 
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    '<div class="cell-content">🟦</div>', 
                                    unsafe_allow_html=True
                                )
                        elif st.session_state.game['game_over'] and (row, col) == st.session_state.game['mine_position']:
                            st.markdown(
                                '<div class="cell-content mine-cell">💣</div>', 
                                unsafe_allow_html=True
                            )
                        elif (row, col) in st.session_state.game['opened']:
                            st.markdown(
                                '<div class="cell-content safe-cell">💰</div>', 
                                unsafe_allow_html=True
                            )
                        else:
                            st.button(
                                "🟦",
                                key=f"cell_{row}_{col}",
                                on_click=open_cell, 
                                args=(row, col),
                                help="Нажмите, чтобы открыть клетку"
                            )
    
    # Кнопки управления
    if st.session_state.game['game_over']:
        st.markdown('<p class="game-over">Вы нашли мину! Игра окончена</p>', unsafe_allow_html=True)
        if st.button("🔄 Продолжить", type="primary", key="continue"):
            continue_after_mine()
    elif not st.session_state.game['first_move']:
        if st.button("🏦 Забрать выигрыш", type="primary", key="cash_out"):
            cash_out()

# Правила игры
with st.expander("📖 Правила игры"):
    st.write("""
    1. Минимальная ставка: 10 ⭐️
    2. Открывайте клетки на поле 5x5
    3. В безопасных клетках множитель увеличивается на 20%
    4. При нахождении мины - игра завершается
    5. Можно забрать выигрыш после первого хода
    6. 💣 - найденная мина
    7. 💥 - другие мины на поле
    8. 💰 - безопасные открытые клетки
    9. 🟦 - неоткрытые клетки
    """)
with st.expander("🔗 Реферальная программа"):
    st.write(f"""
    💬 Приглашай друзей по своей ссылке:\n
    https://t.me/AppYourSiteBot/id=\n\n
    ✅ И получай бонусы!\n
    """)
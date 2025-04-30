import streamlit as st
import random

st.title("🎰 Nvuti - Кастомная Рулетка")

st.write("""
**Правила игры:**
1. Выберите вероятность выигрыша (от 1% до 99%)
2. Сделайте ставку (виртуальные кредиты)
3. Выберите "меньше" или "больше"
4. Проверьте, угадали ли вы!
""")

# Инициализация баланса в сессии
if 'balance' not in st.session_state:
    st.session_state.balance = 1000

# Функция для игры
def play_game(chance, bet, choice):
    # Генерация случайного числа
    random_number = random.randint(0, 999999)
    threshold = 999999 * (chance / 100) if choice == "меньше" else 999999 * ((100 - chance) / 100)
    
    # Определение победы
    if (choice == "меньше" and random_number < threshold) or (choice == "больше" and random_number > threshold):
        win_amount = bet * ((100 - chance) / chance) if choice == "меньше" else bet * (chance / (100 - chance))
        st.session_state.balance += win_amount
        return f"🎉 Победа! Выпало число: {random_number}. Вы выиграли: {win_amount:.2f} кредитов!"
    else:
        st.session_state.balance -= bet
        return f"💥 Проигрыш! Выпало число: {random_number}. Вы потеряли: {bet} кредитов."

# Интерфейс
col1, col2 = st.columns(2)

min_bet = 10
with col1:
    chance = st.slider("Шанс на победу (%)", 1, 99, 50)
    if st.session_state.balance >= min_bet:
        bet = st.number_input("Сумма ставки", min_value=min_bet, step=5, max_value=int(st.session_state.balance), value=100)
    else:
        st.write("Недостаточно средств, пополните баланс!")

with col2:
    choice = st.radio("Выберите:", ["меньше", "больше"])
    st.write(f"Текущий баланс: {int(st.session_state.balance)} кредитов")
    
if st.session_state.balance >= min_bet:
    if st.button("Сделать ставку"):
        result = play_game(chance, bet, choice)
        st.write(result)
        st.write(f"Новый баланс: {int(st.session_state.balance)} кредитов")

st.warning("⚠️ Вы сможете заработать тут кучу денег!")
import sqlite3
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

# підключення до бази даних або створення якщо не існує
db_name = 'spam_db.sqlite'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        is_spam INTEGER NOT NULL
    )
''')

cursor.execute('SELECT COUNT(*) FROM messages')
count = cursor.fetchone()[0]

if count == 0:  # Заповнюємо початкові дані якщо таблиця порожня
    data = [
        # СПАМ
        ("Ви виграли iPhone! Натисніть сюди!", 1),
        ("Отримайте кредит за 5 хвилин!", 1),
        ("Купи зараз — знижка 70%", 1),
        ("Ваш рахунок заблоковано. Увійдіть негайно!", 1),
        ("Ексклюзивна пропозиція тільки сьогодні!", 1),
        ("Безкоштовний подарунок для вас!", 1),
        ("Натисніть тут, щоб отримати приз!", 1),
        ("Заробляйте $5000 за тиждень не виходячи з дому!", 1),
        ("Легкі гроші без вкладень!", 1),
        ("Ваш аккаунт буде видалено, якщо ви не підтвердите дані!", 1),
        ("Самотні дівчата-супермоделі чекають на зустріч з тобою!", 1),

        # НЕ СПАМ
        ("Зустрінемось о 18:00 в кав’ярні?", 0),
        ("Не забудь про дзвінок мамі", 0),
        ("Дякую за допомогу!", 0),
        ("Нагадуємо про зустріч завтра", 0),
        ("Привіт! Як справи?", 0),
        ("Плануємо поїздку на вихідних.", 0),
        ("Чи можеш надіслати мені той файл?", 0),
        ("Погода сьогодні чудова для прогулянки.", 0),
        ("Вітаю з днем народження!", 0),
        ("Потрібна допомога з домашнім завданням?", 0),
        ("Погодуй кота!", 0)
    ]
    cursor.executemany('INSERT INTO messages (text, is_spam) VALUES (?, ?)', data)
    conn.commit()

# Завантажуємо всі дані для навчання моделі та закриваємо підключення до бази
cursor.execute('SELECT text, is_spam FROM messages')
rows = cursor.fetchall()
conn.close()

# Розділяємо дані на вхідні тексти та мітки (1 - спам, 0 - не спам)
texts = [row[0] for row in rows]
labels = [row[1] for row in rows]

# Vectorizer — перетворює тексти у числові вектори (матричне представлення)
# CountVectorizer рахує, скільки разів кожне слово зустрічається у повідомленні
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts) # навчаємось на всіх текстах (побудова словника)

# Створюємо і навчаємо модель (Naive Bayes classifier) для класифікації текстів
# MultinomialNB добре підходить для текстових даних із підрахунком частоти слів
model = MultinomialNB()
model.fit(X, labels)                # Навчаємо модель на векторизованих текстах і мітках

# ввід користувача і перевірка
print("Перевірка фраз на СПАМ")
print("Введіть фразу (Ctrl+C для виходу):")

try:
    while True:
        user_input = input("> ")

        # Перетворюємо текст користувача у вектор за допомогою навченого векторизатора
        user_vector = vectorizer.transform([user_input])

        # Передбачаємо, чи є повідомлення спамом (1) чи ні (0)
        prediction = model.predict(user_vector)

        if prediction[0] == 1:
            print("Це схоже на СПАМ!")
        else:
            print("Це нормальне повідомлення)")
except KeyboardInterrupt:
    print("\nПа-па!")
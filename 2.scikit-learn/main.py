import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# 1. Отримання даних з API НБУ
def fetch_usd_rates(date_start, date_end):
    current = date_start
    data = []

    while current <= date_end:
        date_string = current.strftime('%Y%m%d')
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&date={date_string}&json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            daily_data = response.json()
            if daily_data:
                usd_rate = daily_data[0]['rate']
                data.append({'date': current, 'rate': usd_rate})
        except Exception as e:
            print(f"Помилка отримання курсу на дату {date_string}: {e}")
        current += timedelta(days=1)

    return pd.DataFrame(data)

# 2. Завантаження даних за останній місяць
start_date = datetime.today() - timedelta(days=30)
end_date = datetime.today()
df = fetch_usd_rates(start_date, end_date)

if df.empty:
    print("Не вдалося отримати дані по API НБУ(")
    exit(1)

# 3. Підготовка даних для моделі
df['day_number'] = (df['date'] - df['date'].min()).dt.days
X = df[['day_number']]
y = df['rate']

# 4. Побудова та навчання моделі
model = LinearRegression()
model.fit(X, y)

# 5. Прогноз на 10 днів
last_day = df['day_number'].max()
future_days = np.array([last_day + i for i in range(1, 11)]).reshape(-1, 1)
future_dates = [df['date'].max() + timedelta(days=i) for i in range(1, 11)]
future_rates = model.predict(pd.DataFrame(future_days, columns=['day_number']))

# 6. Додаємо останню точку історії до прогнозу для безперервного графіка
last_date = df['date'].max()
last_rate = df[df['date'] == last_date]['rate'].values[0]
last_day_num = df[df['date'] == last_date]['day_number'].values[0]

forecast_df = pd.DataFrame({
    'date': [last_date] + future_dates,
    'rate': [last_rate] + list(future_rates),
    'day_number': [last_day_num] + list(future_days.flatten())
})

# 7. Об'єднання історичних та прогнозованих даних
full_df = pd.concat([df[['date', 'rate', 'day_number']], forecast_df.iloc[1:]])  # щоб не дублювати останню точку

# 8. Збереження у CSV
full_df['date'] = full_df['date'].dt.date
full_df = full_df[['day_number', 'date', 'rate']]
full_df.to_csv("usd_uah_nbu_rates.csv", index=False)

# 9. Вивід прогнозу
print("\nПрогноз курсу USD/UAH на 10 днів:")
for date, rate in zip(future_dates, future_rates):
    print(f"{date.date()}: {rate:.2f} грн.")

# 10. Побудова графіка
plt.figure(figsize=(10, 5))

# Історичні дані - синя лінія
plt.plot(df['date'], df['rate'], label='Історичний курс', color='blue')

# Прогноз (від останньої історичної точки) - суцільна товста червона лінія
plt.plot(forecast_df['date'], forecast_df['rate'], 'r-', label='Прогноз', linewidth=3)

plt.xlabel("Дата")
plt.ylabel("Курс USD/UAH")
plt.title("Прогноз курсу долара (НБУ) на 10 днів")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
import datetime


def check_task_date(date):
    if isinstance(date, str):
        date = date.split(".")
        if len(date) < 3: return False
        if not date[0].isdigit() or not date[1].isdigit() or not date[2].isdigit(): return False
        day = int(date[0])
        month = int(date[1])
        year = int(date[2])
    elif isinstance(date, dict):
        day = date["day"]
        month = date["month"]
        year = date["year"]
    else:
        print("Функция check_task_date(date) приняла неверные аргументы.")
        return False

    today = datetime.datetime.today()

    month_day = {1: 31,
                 2: 28,
                 3: 31,
                 4: 30,
                 5: 31,
                 6: 30,
                 7: 31,
                 8: 31,
                 9: 30,
                 10: 31,
                 11: 30,
                 12: 31}
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0): month_day[2] = 29

    if not 1 <= month <= 12: return False
    if not 1 <= day <= month_day[month]: return False
    if year < today.year: return False
    if year == today.year and month < today.month: return False
    if year == today.year and month == today.month and day < today.day: return False
    return True


if __name__ == "__main__":
    print("Файл должен быть импортирован")

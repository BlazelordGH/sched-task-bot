import datetime


def check_task_time(date, time):
    if isinstance(time, str):
        if ":" not in time: return False
        time = time.split(":")
        if len(time) != 2: return False
        if not time[0].isdigit() or not time[1].isdigit(): return False
        if len(time[1]) == 1: return False
        hour = int(time[0])
        minute = int(time[1])
    elif isinstance(time, dict):
        hour = time["hour"]
        minute = time["minute"]
    else:
        print("Функция check_task_time(date, time) приняла неверные аргументы.")
        return False

    today_date = datetime.datetime.today()
    today_time = datetime.datetime.now().time()

    if not 0 <= hour <= 23 or not 0 <= minute <= 59: return False
    if date["day"] == today_date.day and date["month"] == today_date.month and date["year"] == today_date.year:
        if hour < today_time.hour:
            return False
        elif hour == today_time.hour and minute <= today_time.minute:
            return False
    return True


if __name__ == "__main__":
    print("Файл должен быть импортирован")

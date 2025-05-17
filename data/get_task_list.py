def format_date(date):
    day = str(date["day"])
    if len(day) == 1: day = "0" + day
    month = str(date["month"])
    if len(month) == 1: month = "0" + month
    year = date["year"]

    return f"{day}.{month}.{year}"


def format_time(time):
    hour = str(time["hour"])
    if len(hour) == 1: hour = "0" + hour
    minute = str(time["minute"])
    if len(minute) == 1: minute = "0" + minute

    return f"{hour}:{minute}"


def get_task_list(tasks_list):
    text = ""
    for i in range(len(tasks_list)):
        text += f'{i + 1}. {tasks_list[i]["name"]} – {format_date(tasks_list[i]["date"])} – {format_time(tasks_list[i]["time"])}\n'
    return text


if __name__ == "__main__":
    print("Файл должен быть импортирован")

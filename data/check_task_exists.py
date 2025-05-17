def check_task_exists(cur_task, tasks):
    for task in tasks:
        if cur_task["name"].lower() == task["name"].lower() and \
            cur_task["date"] == task["date"] and \
            cur_task["time"] == task["time"]:
            return True
    return False


if __name__ == "__main__":
    print("Файл должен быть импортирован")

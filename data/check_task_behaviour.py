def check_task_behaviour(behaviour):
    if behaviour != "Один раз" and behaviour != "Постоянно": return False
    return True


if __name__ == "__main__":
    print("Файл должен быть импортирован")

def check_task_num(num, tasks_list):
    if not num.isdigit(): return False

    if 1 <= int(num) <= len(tasks_list):
        return True
    return False


def delete_task(num, tasks_list):
    new_tasks_list = []
    for i in range(len(tasks_list)):
        if i == num - 1:
            continue
        new_tasks_list.append(tasks_list[i])
    return new_tasks_list


if __name__ == "__main__":
    print("Файл должен быть импортирован")

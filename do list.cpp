#include <iostream>
#include <vector>
#include <string>

struct Task {
    std::string description;
    bool toxic;

    Task(const std::string& desc, bool tox) : description(desc), toxic(tox) {}
};

class ToDoList {
private:
    std::vector<Task> tasks;

public:
    void addTask(const std::string& desc, bool tox) {
        tasks.push_back(Task(desc, tox));
        std::cout << "Task added successfully." << std::endl;
    }

    void deleteTask(int index) {
        if (index >= 0 && index < tasks.size()) {
            tasks.erase(tasks.begin() + index);
            std::cout << "Task deleted successfully." << std::endl;
        } else {
            std::cout << "Invalid task index." << std::endl;
        }
    }

    void displayTasks() {
        if (tasks.empty()) {
            std::cout << "No tasks to display." << std::endl;
        } else {
            std::cout << "Tasks:" << std::endl;
            for (size_t i = 0; i < tasks.size(); ++i) {
                std::cout << i << ". " << tasks[i].description;
                if (tasks[i].toxic) {
                    std::cout << " [TOXIC]";
                }
                std::cout << std::endl;
            }
        }
    }
};

int main() {
    ToDoList todo;
    int choice;
    std::string desc;
    bool tox;

    do {
        std::cout << "\n1. Add Task\n2. Delete Task\n3. Display Tasks\n4. Exit\nEnter your choice: ";
        std::cin >> choice;

        switch (choice) {
            case 1:
                std::cout << "Enter task description: ";
                std::cin.ignore();
                std::getline(std::cin, desc);
                std::cout << "Is this task toxic? (1 for Yes, 0 for No): ";
                std::cin >> tox;
                todo.addTask(desc, tox);
                break;
            case 2:
                int index;
                std::cout << "Enter task index to delete: ";
                std::cin >> index;
                todo.deleteTask(index);
                break;
            case 3:
                todo.displayTasks();
                break;
            case 4:
                std::cout << "Exiting program." << std::endl;
                break;
            default:
                std::cout << "Invalid choice. Please try again." << std::endl;
        }
    } while (choice != 4);

    return 0;
}

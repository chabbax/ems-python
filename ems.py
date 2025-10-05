# Author: Chandur Dissanayake
# Student ID: 1860963
# Github:
#
# Installation prerequisites
#
# Requirements
#   - Python 3.8+
#   - Internet access only needed to install 'rich' library and is not required afterwards.
#
# macOS / Linux
#   - python3 -m kbs .kbs
#   - source .kbs/bin/activate
#   - python -m pip install --upgrade pip
#   - python -m pip install rich
#   - python 1860963.py
#   - deactivate
#
# Windows (CMD)
#   - py -m kbs .kbs
#   - .kbs\Scripts\activate.bat
#   - pip install --upgrade pip
#   - pip install rich
#   - py 1860963.py
#   - deactivate
#
# Notes
#   - Data files are created in the program folder:
#       - Current_Employees.pkl
#       - Current_Employees.json
#   - If 'rich' isn't installed, the program still runs with plain console output.
#   - Always run the program from the same folder as the script so the data files are found.

import os
import re
import json
import pickle
import random
from datetime import datetime

# Rich (coloured output); falls back to plain prints if unavailable
try:
    from rich import box
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
    console = Console()
except Exception:
    RICH_AVAILABLE = False
    console = None

# Styles for Rich
RICH_STYLES = {
    "title": "bold cyan",
    "header": "bold magenta",
    "ok": "bold green",
    "info": "cyan",
    "warn": "yellow",
    "error": "bold red",
    "name": "bold white",
    "position": "bold cyan",
    "salary": "green",
    "email": "red",
    "created": "yellow",
    "updated": "yellow",
    "id": "bold white",
}

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
PICKLE_FILE = "Current_Employees.pkl"
JSON_SNAPSHOT_FILE = "Current_Employees.json"

ALLOWED_POSITIONS = ("Manager", "Developer", "Designer", "Analyst", "HR")
ALLOWED_DEPARTMENTS = ("IT", "Design", "Finance", "HR", "Operations")
ALLOWED_LOCATIONS = ("Melbourne", "Sydney", "Brisbane", "Adelaide", "Perth")

# -----------------------------------------------------------------------------
# Print helpers
# -----------------------------------------------------------------------------
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_title(text):
    if RICH_AVAILABLE:
        console.rule(Text(text, style=RICH_STYLES["title"]))
    else:
        print(f"\n==== {text} ====\n")

def print_success(text):
    if RICH_AVAILABLE:
        console.print("\n" + text + "\n", style=RICH_STYLES["ok"])
    else:
        print("\n" + text + "\n")

def print_info(text):
    if RICH_AVAILABLE:
        console.print(text, style=RICH_STYLES["info"])
    else:
        print(text)

def print_warning(text):
    if RICH_AVAILABLE:
        console.print(text, style=RICH_STYLES["warn"])
    else:
        print(f"WARNING: {text}")

def print_error(text):
    if RICH_AVAILABLE:
        console.print(text, style=RICH_STYLES["error"])
    else:
        print(f"ERROR: {text}")

def get_last_modified_text(path):
    if not os.path.exists(path):
        return "n/a"
    try:
        return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "n/a"

def print_last_modified_summary():
    pkl_ts = get_last_modified_text(PICKLE_FILE)
    json_ts = get_last_modified_text(JSON_SNAPSHOT_FILE)
    if os.path.exists(PICKLE_FILE) and os.path.exists(JSON_SNAPSHOT_FILE):
        print_info(f"Last modified — Pickle: {pkl_ts} | JSON: {json_ts}")
    elif os.path.exists(JSON_SNAPSHOT_FILE):
        print_info(f"Last modified — JSON: {json_ts}")
    elif os.path.exists(PICKLE_FILE):
        print_info(f"Last modified — Pickle: {pkl_ts}")

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
class Validation:
    EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$')
    AGE_REGEX = re.compile(r'^(1[6-9]|[2-6][0-9]|70)$')  # 16–70

    @staticmethod
    def normalize(text):
        return str(text).strip().casefold()

    @staticmethod
    def is_cancel_text(text):
        return str(text).strip().lower() == "q"

    @staticmethod
    def prompt_non_empty(message_text, allow_cancel=False):
        while True:
            try:
                text = input(message_text).strip()
            except EOFError:
                return None if allow_cancel else ""
            if allow_cancel and Validation.is_cancel_text(text):
                return None
            if text == "":
                print_error("Input cannot be empty. Please try again.")
                continue
            return text

    @staticmethod
    def prompt_menu_choice(prompt_text, min_value, max_value, allow_cancel=False):
        while True:
            try:
                text = input(prompt_text).strip()
            except EOFError:
                return None if allow_cancel else min_value
            if allow_cancel and Validation.is_cancel_text(text):
                return None
            if not text or not text.isdigit():
                print_error("Please enter a number using digits only.")
                continue
            number = int(text)
            if number < min_value or number > max_value:
                print_error(f"Enter a number between {min_value} and {max_value}.")
                continue
            return number

    @staticmethod
    def prompt_email(message_text, allow_cancel=False):
        while True:
            text = Validation.prompt_non_empty(message_text, allow_cancel=allow_cancel)
            if text is None:
                return None
            if Validation.EMAIL_REGEX.fullmatch(text):
                return text
            print_error("Please enter a valid email address (e.g., name@example.com).")

    @staticmethod
    def prompt_age(message_text, allow_cancel=False):
        while True:
            text = Validation.prompt_non_empty(message_text, allow_cancel=allow_cancel)
            if text is None:
                return None
            if Validation.AGE_REGEX.fullmatch(text):
                return int(text)
            print_error("Age must be between 16 and 70 (digits only).")

    @staticmethod
    def prompt_float(message_text, allow_cancel=False):
        while True:
            text = Validation.prompt_non_empty(message_text, allow_cancel=allow_cancel)
            if text is None:
                return None
            try:
                return float(text)
            except ValueError:
                print_error("Please enter a number (e.g., 75000 or 75000.0).")

# -----------------------------------------------------------------------------
# Employee model
# -----------------------------------------------------------------------------
class Employee:
    def __init__(self, name, age, position, salary, department, location, email, employee_id):
        self.__name = name
        self.__age = age
        self.__position = position
        self.__salary = salary
        self.department = department
        self.location = location
        self.email = email
        self.employee_id = employee_id
        self.created_at = now_text()
        self.updated_at = None

    def get_name(self): return self.__name
    def get_age(self): return self.__age
    def get_position(self): return self.__position
    def get_salary(self): return self.__salary
    def set_name(self, v): self.__name = v
    def set_age(self, v): self.__age = v
    def set_position(self, v): self.__position = v
    def set_salary(self, v): self.__salary = float(v)

    def to_dict(self):
        return {
            "name": self.__name,
            "age": self.__age,
            "position": self.__position,
            "salary": self.__salary,
            "department": self.department,
            "location": self.location,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

# -----------------------------------------------------------------------------
# Simple sorting helpers (no lambdas)
# -----------------------------------------------------------------------------
def sort_pairs_by_id(pairs):
    """Bubble-sort a list of (id, Employee) by id ascending."""
    result = pairs[:]
    n = len(result)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if result[j][0] > result[j + 1][0]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result

def sort_pairs_by_salary(pairs, descending=False):
    """Bubble-sort by salary."""
    result = pairs[:]
    n = len(result)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            a = float(result[j][1].get_salary())
            b = float(result[j + 1][1].get_salary())
            swap_needed = (a < b) if descending else (a > b)
            if swap_needed:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result

def sort_pairs_by_name(pairs):
    """Bubble-sort by name (case-insensitive)."""
    result = pairs[:]
    n = len(result)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            a = Validation.normalize(result[j][1].get_name())
            b = Validation.normalize(result[j + 1][1].get_name())
            if a > b:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result

def sort_pairs_by_position_random(pairs, allowed_positions):
    """
    Group by a randomised order of positions; inside each group sort by name.
    Returns (sorted_pairs, order_used).
    """
    positions = list(allowed_positions)
    random.shuffle(positions)
    grouped = []
    # Add known positions in the random order
    for pos in positions:
        group = []
        for emp_id, emp in pairs:
            if emp.get_position() == pos:
                group.append((emp_id, emp))
        group = sort_pairs_by_name(group)
        grouped.extend(group)
    # Add any unknown positions at the end (also sorted by name)
    others = []
    for emp_id, emp in pairs:
        if emp.get_position() not in positions:
            others.append((emp_id, emp))
    others = sort_pairs_by_name(others)
    grouped.extend(others)
    return grouped, positions

# -----------------------------------------------------------------------------
# Persistence (pickle + JSON snapshot)
# -----------------------------------------------------------------------------
def load_all_records():
    if not os.path.exists(PICKLE_FILE):
        return {}
    try:
        with open(PICKLE_FILE, "rb") as fh:
            data = pickle.load(fh)
            return data if isinstance(data, dict) else {}
    except (OSError, EOFError, pickle.UnpicklingError):
        return {}

def export_json_snapshot(records_dict, json_file=JSON_SNAPSHOT_FILE):
    try:
        as_dict = {emp_id: emp.to_dict() for emp_id, emp in records_dict.items()}
        with open(json_file, "w", encoding="utf-8") as jh:
            json.dump(as_dict, jh, indent=2)
    except Exception as e:
        print_warning(f"Snapshot export failed: {e}")

def save_all_records(records_dict):
    with open(PICKLE_FILE, "wb") as fh:
        pickle.dump(records_dict, fh)
    export_json_snapshot(records_dict)

def next_sequential_id(records_dict):
    max_num = 0
    for emp_id in records_dict.keys():
        if str(emp_id).isdigit():
            n = int(emp_id)
            if n > max_num:
                max_num = n
    return str(max_num + 1).zfill(3)

def seed_defaults_if_empty():
    data = load_all_records()
    if data:
        return
    data = {
        "001": Employee("Olivia Brown", 34, "Manager", 125000.0, "IT", "Melbourne",
                        "olivia.brown@example.com", "001"),
        "002": Employee("Noah Wilson", 28, "Developer", 98000.0, "Operations", "Sydney",
                        "noah.wilson@example.com", "002"),
        "003": Employee("Ava Thompson", 31, "Designer", 86000.0, "Design", "Brisbane",
                        "ava.thompson@example.com", "003"),
        "004": Employee("Liam Taylor", 26, "Analyst", 90000.0, "Finance", "Adelaide",
                        "liam.taylor@example.com", "004"),
    }
    save_all_records(data)
    print_success("Employee file initialized with seed records (IDs 001–004)")
    print_info("Pickle (live) and JSON snapshot are both up to date")
    print_last_modified_summary()

# -----------------------------------------------------------------------------
# Responsive table
# -----------------------------------------------------------------------------
def print_table(title_text, records_dict, preserve_order=False):
    if not records_dict:
        print_info("No records found.")
        return

    items = list(records_dict.items())
    if not preserve_order:
        items = sort_pairs_by_id(items)

    if not RICH_AVAILABLE:
        print(title_text)
        for emp_id, emp in items:
            print(f"- [{emp_id}] {emp.get_name()} ({emp.get_age()}) - {emp.get_position()} "
                  f"@ {emp.department}/{emp.location} - "
                  f"${float(emp.get_salary()):,.2f} | Created: {emp.created_at} | "
                  f"Updated: {emp.updated_at or '—'}")
        return

    term_width = console.size.width
    compact = term_width < 100

    table = Table(
        title=title_text, box=box.ROUNDED, header_style=RICH_STYLES["header"], expand=True, pad_edge=False
    )

    table.add_column("ID", style=RICH_STYLES["id"], no_wrap=True, min_width=3, justify="left")
    table.add_column("Name", style=RICH_STYLES["name"],
                     min_width=(10 if compact else 14), overflow="fold")
    table.add_column("Age", no_wrap=True, min_width=3, justify="right")
    table.add_column("Position", style=RICH_STYLES["position"],
                     min_width=(8 if compact else 10), overflow="fold")
    table.add_column("Salary", style=RICH_STYLES["salary"], justify="right",
                     min_width=(12 if compact else 16), overflow="fold")
    table.add_column("Department", min_width=(7 if compact else 9), overflow="fold")
    table.add_column("Location", min_width=(7 if compact else 9), overflow="fold")
    table.add_column("Email", style=RICH_STYLES["email"],
                     min_width=(18 if compact else 26), overflow="fold")
    table.add_column("Created", style=RICH_STYLES["created"],
                     min_width=(16 if compact else 19), overflow="fold")
    table.add_column("Updated", style=RICH_STYLES["updated"],
                     min_width=(16 if compact else 19), overflow="fold")

    for emp_id, emp in items:
        table.add_row(
            emp_id,
            str(emp.get_name()),
            str(emp.get_age()),
            str(emp.get_position()),
            f"${float(emp.get_salary()):,.2f}",
            str(emp.department),
            str(emp.location),
            str(emp.email),
            str(emp.created_at),
            str(emp.updated_at or "—"),
        )
    console.print(table)

# -----------------------------------------------------------------------------
# Menu UI
# -----------------------------------------------------------------------------
def show_welcome_message():
    message = (
        "Welcome to the Employee Management System\n\n"
        "• After each change we also export a JSON snapshot for sharing/reporting.\n"
        "• Seed IDs 001–004. New employees get 005, 006, ...\n"
        "• Use the menu to Add, View, Update by ID, Delete by ID, Search, or Sort.\n"
        "• Type 'Q' at any prompt to cancel and return to the main menu.\n"
        "• After each change, the files’ last modified times are shown."
    )
    if RICH_AVAILABLE:
        console.print(Panel(message, title="Welcome", border_style=RICH_STYLES["title"]))
    else:
        print("\n" + message + "\n")

def show_menu(has_records):
    lines = [
        "Employee Management System",
        "1) Add Employee",
        "2) View All Employees",
        "3) Update Employee",
        "4) Delete Employee",
        "5) Search Employee",
        "6) Sort Employees",
        "7) Exit",
    ]
    body = "\n".join(lines)
    if RICH_AVAILABLE:
        console.print(Panel(body, title="Menu", border_style=RICH_STYLES["title"]))
    else:
        print("\n" + body + "\n")

def choose_from_indexed(label, options_tuple, allow_cancel=False):
    body_lines = [f"{i}) {opt}" for i, opt in enumerate(options_tuple, start=1)]
    body = "\n".join(body_lines)
    if RICH_AVAILABLE:
        console.print(Panel(body, title=label, border_style=RICH_STYLES["title"]))
    else:
        print(f"\n{label}\n{body}\n")
    choice = Validation.prompt_menu_choice(f"Enter number (1-{len(options_tuple)}): ",
                                           1, len(options_tuple), allow_cancel=allow_cancel)
    if choice is None:
        return None
    return options_tuple[choice - 1]

# -----------------------------------------------------------------------------
# CRUD + Search/Sort
# -----------------------------------------------------------------------------
def add_employee():
    data = load_all_records()
    print_title("Add Employee")
    print_info("Tip: type 'Q' at any prompt to cancel and return to the main menu.")

    name_set = {Validation.normalize(emp.get_name()) for emp in data.values()}

    while True:
        name_value = Validation.prompt_non_empty("Name: ", allow_cancel=True)
        if name_value is None:
            print_info("Add cancelled."); return
        if Validation.normalize(name_value) in name_set:
            print_error("An employee with this name already exists. Enter a different name.")
            continue
        break

    age_value = Validation.prompt_age("Age (16–70): ", allow_cancel=True)
    if age_value is None:
        print_info("Add cancelled."); return

    position_value = choose_from_indexed("Choose Position", ALLOWED_POSITIONS, allow_cancel=True)
    if position_value is None:
        print_info("Add cancelled."); return

    salary_value = Validation.prompt_float("Salary (number): ", allow_cancel=True)
    if salary_value is None:
        print_info("Add cancelled."); return

    department_value = choose_from_indexed("Choose Department", ALLOWED_DEPARTMENTS, allow_cancel=True)
    if department_value is None:
        print_info("Add cancelled."); return

    location_value = choose_from_indexed("Choose Location", ALLOWED_LOCATIONS, allow_cancel=True)
    if location_value is None:
        print_info("Add cancelled."); return

    email_value = Validation.prompt_email("Contact email: ", allow_cancel=True)
    if email_value is None:
        print_info("Add cancelled."); return

    new_id = next_sequential_id(data)
    emp = Employee(name_value, age_value, position_value, salary_value,
                   department_value, location_value, email_value, employee_id=new_id)

    data[new_id] = emp
    save_all_records(data)
    print_success(f"Employee [{new_id}] '{name_value}' added successfully.")
    print_last_modified_summary()

def view_all_employees():
    print_title("All Current Employees")
    data = load_all_records()
    print_table("Current Employees", data)

def update_employee():
    data = load_all_records()
    if not data:
        print_info("No records to update."); return

    print_title("Update Employee (by ID)")
    print_info("Tip: type 'Q' at any prompt to cancel and return to the main menu.")
    target_id = Validation.prompt_non_empty("Enter the EMPLOYEE ID to update: ", allow_cancel=True)
    if target_id is None or target_id not in data:
        print_info("Update cancelled or ID not found."); return

    emp = data[target_id]
    name_set = {Validation.normalize(e.get_name()) for k, e in data.items() if k != target_id}

    changed = False
    while True:
        if RICH_AVAILABLE:
            info_lines = [
                "1) Name       : " + str(emp.get_name()),
                "2) Age        : " + str(emp.get_age()),
                "3) Position   : " + str(emp.get_position()),
                "4) Salary     : " + f"${float(emp.get_salary()):,.2f}",
                "5) Department : " + str(emp.department),
                "6) Location   : " + str(emp.location),
                "7) Email      : " + str(emp.email),
                "8) Done"
            ]
            console.print(Panel("\n".join(info_lines), title=f"Edit Employee [{target_id}] Fields",
                                border_style=RICH_STYLES["title"]))
        else:
            print("1) Name\n2) Age\n3) Position\n4) Salary\n5) Department\n6) Location\n7) Email\n8) Done")

        choice = Validation.prompt_menu_choice("Choose a field (1-8): ", 1, 8, allow_cancel=True)
        if choice is None:
            print_info("Update cancelled."); return
        if choice == 8:
            break

        if choice == 1:
            new_name = Validation.prompt_non_empty("New name: ", allow_cancel=True)
            if new_name is None:
                continue
            if Validation.normalize(new_name) in name_set:
                print_error("Another employee with this name already exists.")
                continue
            emp.set_name(new_name); changed = True

        elif choice == 2:
            new_age = Validation.prompt_age("New age (16–70): ", allow_cancel=True)
            if new_age is None:
                continue
            emp.set_age(new_age); changed = True

        elif choice == 3:
            new_pos = choose_from_indexed("Choose New Position", ALLOWED_POSITIONS, allow_cancel=True)
            if new_pos is None:
                continue
            emp.set_position(new_pos); changed = True

        elif choice == 4:
            new_sal = Validation.prompt_float("New salary: ", allow_cancel=True)
            if new_sal is None:
                continue
            emp.set_salary(new_sal); changed = True

        elif choice == 5:
            new_dept = choose_from_indexed("Choose New Department", ALLOWED_DEPARTMENTS, allow_cancel=True)
            if new_dept is None:
                continue
            emp.department = new_dept; changed = True

        elif choice == 6:
            new_loc = choose_from_indexed("Choose New Location", ALLOWED_LOCATIONS, allow_cancel=True)
            if new_loc is None:
                continue
            emp.location = new_loc; changed = True

        elif choice == 7:
            new_email = Validation.prompt_email("New email: ", allow_cancel=True)
            if new_email is None:
                continue
            emp.email = new_email; changed = True

        if changed:
            emp.updated_at = now_text()
            print_success("Field updated. Choose another field or select 'Done'.")

    if changed:
        data[target_id] = emp
        save_all_records(data)
        print_success(f"Employee [{target_id}] updated successfully.")
        print_last_modified_summary()
    else:
        print_info("No changes made.")

def delete_employee():
    data = load_all_records()
    if not data:
        print_info("No records to delete."); return

    print_title("Delete Employee (by ID)")
    print_info("Tip: type 'Q' at any prompt to cancel and return to the main menu.")
    target_id = Validation.prompt_non_empty("Enter the EMPLOYEE ID to delete: ", allow_cancel=True)
    if target_id is None or target_id not in data:
        print_info("Delete cancelled or ID not found."); return

    emp = data[target_id]
    print_warning(f"About to delete [{target_id}] {emp.get_name()} — "
                  f"{emp.get_position()} ({emp.department}/{emp.location})")
    confirm = Validation.prompt_non_empty("Are you sure you want to delete? (y/n): ", allow_cancel=True)
    if confirm is None or confirm.lower() != "y":
        print_info("Delete cancelled."); return

    del data[target_id]
    save_all_records(data)
    print_success(f"Employee [{target_id}] '{emp.get_name()}' deleted successfully.")
    print_last_modified_summary()

def search_employee():
    print_title("Search Employee")
    print_info("Tip: type 'Q' at any prompt to cancel and return to the main menu.")
    data = load_all_records()
    if not data:
        print_info("No records to search."); return

    mode = choose_from_indexed("Search by", ("ID", "Name"), allow_cancel=True)
    if mode is None:
        print_info("Search cancelled."); return

    if mode == "ID":
        q = Validation.prompt_non_empty("Enter Employee ID: ", allow_cancel=True)
        if q is None:
            print_info("Search cancelled."); return
        results = {q: data[q]} if q in data else {}
    else:
        q = Validation.prompt_non_empty("Enter Name (exact, case-insensitive): ", allow_cancel=True)
        if q is None:
            print_info("Search cancelled."); return
        qn = Validation.normalize(q)
        results = {}
        for emp_id, emp in data.items():
            if Validation.normalize(emp.get_name()) == qn:
                results[emp_id] = emp

    if not results:
        print_info("No matches."); return
    print_table("Search Results", results)

def sort_employees():
    """
    Sort by Salary or Position.
      • Salary: 'Lowest to Largest' / 'Largest to Lowest'.
      • Position: RANDOMISED group order each time (shows 'random').
    """
    data = load_all_records()
    if not data:
        print_info("No records to sort."); return

    print_title("Sort Employees")
    print_info("Tip: type 'Q' at any prompt to cancel and return to the main menu.")

    sort_field = choose_from_indexed("Sort by", ("Salary", "Position"), allow_cancel=True)
    if sort_field is None:
        print_info("Sort cancelled."); return

    items = list(data.items())

    if sort_field == "Salary":
        order_choice = choose_from_indexed("Order", ("Lowest to Largest", "Largest to Lowest"), allow_cancel=True)
        if order_choice is None:
            print_info("Sort cancelled."); return
        is_desc = (order_choice == "Largest to Lowest")
        items = sort_pairs_by_salary(items, descending=is_desc)
    else:
        items, order_used = sort_pairs_by_position_random(items, ALLOWED_POSITIONS)
        print_info("Grouped by position in a random order : " + ", ".join(order_used))

    sorted_view = {}
    for emp_id, emp in items:
        sorted_view[emp_id] = emp
    print_table("Sorted Employees", sorted_view, preserve_order=True)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def show_welcome_message_and_seed():
    show_welcome_message()
    seed_defaults_if_empty()

def export_snapshot_and_goodbye():
    data = load_all_records()
    export_json_snapshot(data, JSON_SNAPSHOT_FILE)
    print_info(f"List of employee snapshot exported to {JSON_SNAPSHOT_FILE}")
    print_last_modified_summary()
    print_info("Thank you for using the Employee Management System!")

def main():
    show_welcome_message_and_seed()
    while True:
        has_records = bool(load_all_records())
        show_menu(has_records)
        selection = Validation.prompt_menu_choice("Choose an option (1-7): ", 1, 7, allow_cancel=True)
        if selection is None:
            export_snapshot_and_goodbye()
            break

        if not has_records and selection in (2, 3, 4, 5, 6):
            print_warning("No records yet — please add an employee first.")
            continue

        try:
            if selection == 1: add_employee()
            elif selection == 2: view_all_employees()
            elif selection == 3: update_employee()
            elif selection == 4: delete_employee()
            elif selection == 5: search_employee()
            elif selection == 6: sort_employees()
            elif selection == 7:
                export_snapshot_and_goodbye()
                break
        except Exception as e:
            print_error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

# Employee Management System (EMS) - Educational Purposes

A simple, menu-driven Employee Management System written in Python (Fundamentals of Programming).
It focuses on **OOP**, **file handling**, and **exception handling**.

# Tree Diagram

## Tree diagram of this single-file layout

```bash
 .
 └─ 1860963.py
    |
    ├─ File metadata comments
    │   └─ author, run instructions, notes
    |
    ├─ Imports
    │   ├─ standard library: os, re, json, pickle, random, datetime
    │   └─ third-party: rich (Console, Table, Panel, Text, box)
    |
    ├─ Constants and configuration variables
    │   ├─ PICKLE_FILE, JSON_SNAPSHOT_FILE
    │   ├─ RICH_STYLES
    │   └─ ALLOWED_POSITIONS / DEPARTMENTS / LOCATIONS
    |
    ├─ Printing and time helpers
    │   ├─ now_text()
    │   ├─ print_title(), print_success(), print_info(), print_warning(), print_error()
    │   └─ get_last_modified_text(), print_last_modified_summary()
    |
    ├─ Validation class
    │   └─ EMAIL_REGEX, AGE_REGEX, normalize(), is_cancel_text(), prompt_non_empty(),
    │      prompt_menu_choice(), prompt_email(), prompt_age(), prompt_float()
    |
    ├─ Employee class
    │   └─ __init__(), getters and setters, to_dict()
    |
    ├─ Sorting helpers
    │   ├─ sort_pairs_by_id()
    │   ├─ sort_pairs_by_salary()
    │   ├─ sort_pairs_by_name()
    │   └─ sort_pairs_by_position_random()
    |
    ├─ Persistence (pickle and JSON)
    │   ├─ load_all_records()
    │   ├─ export_json_snapshot()
    │   ├─ save_all_records()
    │   ├─ next_sequential_id()
    │   └─ seed_defaults_if_empty()
    |
    ├─ UI helpers (table and menu)
    │   ├─ print_table()
    │   ├─ show_welcome_message()
    │   ├─ show_menu()
    │   └─ choose_from_indexed()
    |
    ├─ Features (CRUD, search and sort)
    │   ├─ add_employee()
    │   ├─ view_all_employees()
    │   ├─ update_employee()
    │   ├─ delete_employee()
    │   ├─ search_employee()
    │   └─ sort_employees()
    |
    └─ Entry point
        ├─ show_welcome_message_and_seed()
        ├─ export_snapshot_and_goodbye()
        └─ main()
```

# Prerequisites

- Python 3.10+
- macOS (tested on Apple Silicon/Intel)

## Setup (macOS/linux)

```bash
git clone <repo-url>.git
cd <repo-folder>
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install rich
python main.py
```

To deactivate the venv later:

```bash
deactivate
```

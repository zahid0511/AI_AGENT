import sqlite3

DB_NAME = "employees.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                city TEXT NOT NULL
            )
            """
        )
        conn.commit()


def create_employee(name, email, department, salary, city):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO employees (name, email, department, salary, city)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, department, salary, city)
        )
        conn.commit()
        return {
            "status": "Employee created successfully",
            "employee_id": cursor.lastrowid
        }


def get_employee(employee_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM employees WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_employees():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM employees").fetchall()
        return [dict(row) for row in rows]


def update_employee(employee_id, name, email, department, salary, city):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE employees
            SET name = ?, email = ?, department = ?, salary = ?, city = ?
            WHERE employee_id = ?
            """,
            (name, email, department, salary, city, employee_id)
        )
        conn.commit()
        return {
            "status": "Updated" if cursor.rowcount > 0 else "Employee not found",
            "rows_affected": cursor.rowcount
        }


def delete_employee(employee_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM employees WHERE employee_id = ?",
            (employee_id,)
        )
        conn.commit()
        return {
            "status": "Deleted" if cursor.rowcount > 0 else "Employee not found",
            "rows_affected": cursor.rowcount
        }


def search_by_name(name):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM employees WHERE name LIKE ?",
            (f"%{name}%",)
        ).fetchall()
        return [dict(row) for row in rows]


def search_by_department(department):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM employees WHERE LOWER(department) = LOWER(?)",
            (department,)
        ).fetchall()
        return [dict(row) for row in rows]


def search_by_city(city):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM employees WHERE LOWER(city) = LOWER(?)",
            (city,)
        ).fetchall()
        return [dict(row) for row in rows]


def search_by_salary(minimum_salary, maximum_salary):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM employees WHERE salary BETWEEN ? AND ?",
            (minimum_salary, maximum_salary)
        ).fetchall()
        return [dict(row) for row in rows]


def count_employees():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total_employees FROM employees"
        ).fetchone()
        return dict(row)


def highest_salary():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM employees ORDER BY salary DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def search_department_salary(department, minimum_salary):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM employees
            WHERE LOWER(department) = LOWER(?) AND salary >= ?
            """,
            (department, minimum_salary)
        ).fetchall()
        return [dict(row) for row in rows]

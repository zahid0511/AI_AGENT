import database


database.create_table()


database.create_employee(
    "Rahul",
    "rahul@gmail.com",
    "IT",
    50000,
    "Kolkata"
)


database.create_employee(
    "Priya",
    "priya@gmail.com",
    "HR",
    45000,
    "Delhi"
)


employees = database.get_all_employees()

print(employees)


print(
    database.search_by_department("IT")
)


print(
    database.search_by_city("Kolkata")
)


print(
    database.count_employees()
)


print(
    database.highest_salary()
)

import json
import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

from database import (
    create_employee,
    get_employee,
    get_all_employees,
    update_employee,
    delete_employee,
    search_by_name,
    search_by_department,
    search_by_city,
    search_by_salary,
    count_employees,
    highest_salary,
    search_department_salary
)

# ==========================================
# GEMINI CONFIGURATION
# ==========================================

load_dotenv(find_dotenv(), override=True)

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

MODEL = "gemini-3.6-flash"

# ==========================================
# FUNCTION DECLARATIONS
# ==========================================

tools = [
    {
        "name": "create_employee",
        "description": "Create an employee.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"},
                "email": {"type": "STRING"},
                "department": {"type": "STRING"},
                "salary": {"type": "NUMBER"},
                "city": {"type": "STRING"}
            },
            "required": [
                "name",
                "email",
                "department",
                "salary",
                "city"
            ]
        }
    },
    {
        "name": "get_employee",
        "description": "Get employee using employee ID.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "employee_id": {"type": "INTEGER"}
            },
            "required": ["employee_id"]
        }
    },
    {
        "name": "get_all_employees",
        "description": "Get all employees.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "update_employee",
        "description": "Update an employee.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "employee_id": {"type": "INTEGER"},
                "name": {"type": "STRING"},
                "email": {"type": "STRING"},
                "department": {"type": "STRING"},
                "salary": {"type": "NUMBER"},
                "city": {"type": "STRING"}
            },
            "required": [
                "employee_id",
                "name",
                "email",
                "department",
                "salary",
                "city"
            ]
        }
    },
    {
        "name": "delete_employee",
        "description": "Delete an employee.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "employee_id": {"type": "INTEGER"}
            },
            "required": ["employee_id"]
        }
    },
    {
        "name": "search_by_name",
        "description": "Search employees by partial name.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "search_by_department",
        "description": "Search employees by department.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "department": {"type": "STRING"}
            },
            "required": ["department"]
        }
    },
    {
        "name": "search_by_city",
        "description": "Search employees by city.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "search_by_salary",
        "description": "Search employees within salary range.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "minimum_salary": {"type": "NUMBER"},
                "maximum_salary": {"type": "NUMBER"}
            },
            "required": [
                "minimum_salary",
                "maximum_salary"
            ]
        }
    },
    {
        "name": "count_employees",
        "description": "Count total employees.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "highest_salary",
        "description": "Find employee with highest salary.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "search_department_salary",
        "description": "Find employees in a department earning at least a salary.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "department": {"type": "STRING"},
                "minimum_salary": {"type": "NUMBER"}
            },
            "required": [
                "department",
                "minimum_salary"
            ]
        }
    }
]

# ==========================================
# GEMINI TOOL CONFIGURATION
# ==========================================

gemini_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(**tool)
        for tool in tools
    ]
)

# ==========================================
# PYTHON FUNCTION MAPPING
# ==========================================

tool_functions = {
    "create_employee": create_employee,
    "get_employee": get_employee,
    "get_all_employees": get_all_employees,
    "update_employee": update_employee,
    "delete_employee": delete_employee,
    "search_by_name": search_by_name,
    "search_by_department": search_by_department,
    "search_by_city": search_by_city,
    "search_by_salary": search_by_salary,
    "count_employees": count_employees,
    "highest_salary": highest_salary,
    "search_department_salary": search_department_salary
}

# ==========================================
# AI AGENT
# ==========================================

def ask_agent(user_question):
    input_items = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_question)
            ]
        )
    ]

    while True:
        response = client.models.generate_content(
            model=MODEL,
            contents=input_items,
            config=types.GenerateContentConfig(
                system_instruction="""
                You are an AI employee database assistant.

                Use database tools whenever database
                information or database modification is requested.

                Never invent employee information.
                If updating an employee and only partial fields are given by the user,
                first call get_employee or search_by_name to fetch their existing details
                before calling update_employee.

                Before destructive operations such as DELETE,
                make sure the user's request clearly identifies
                the employee.

                Return a clear natural-language answer.
                """,
                tools=[gemini_tool],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

        # Preserve Gemini response in conversation history
        model_response = response.candidates[0].content
        input_items.append(model_response)

        # No function call means Gemini has completed its response
        if not response.function_calls:
            return response.text

        tool_parts = []

        # Execute function calls
        for item in response.function_calls:
            function_name = item.name
            arguments = dict(item.args)
            function = tool_functions[function_name]

            try:
                result = function(**arguments)
                function_response = {
                    "result": json.loads(
                        json.dumps(result, default=str)
                    )
                }
            except Exception as e:
                function_response = {"error": str(e)}

            tool_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response=function_response
                )
            )

        # Append all tool responses in a single "user" Content block
        input_items.append(
            types.Content(
                role="user",
                parts=tool_parts
            )
        )

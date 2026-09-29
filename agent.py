import json
import os

from openai import OpenAI
from dotenv import load_dotenv,find_dotenv

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

load_dotenv(find_dotenv(),override=True)
client = OpenAI(
    # api_key=os.getenv("OPENAI_API_KEY")
    api_key = os.environ["OPENAI_API_KEY"]
)


tools = [

    {
        "type": "function",
        "name": "create_employee",
        "description": "Create an employee.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "department": {"type": "string"},
                "salary": {"type": "number"},
                "city": {"type": "string"}
            },
            "required": [
                "name",
                "email",
                "department",
                "salary",
                "city"
            ],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_employee",
        "description": "Get employee using employee ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "integer"
                }
            },
            "required": ["employee_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_all_employees",
        "description": "Get all employees.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "update_employee",
        "description": "Update an employee.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "integer"
                },
                "name": {
                    "type": "string"
                },
                "email": {
                    "type": "string"
                },
                "department": {
                    "type": "string"
                },
                "salary": {
                    "type": "number"
                },
                "city": {
                    "type": "string"
                }
            },
            "required": [
                "employee_id",
                "name",
                "email",
                "department",
                "salary",
                "city"
            ],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "delete_employee",
        "description": "Delete an employee.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "integer"
                }
            },
            "required": ["employee_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "search_by_name",
        "description": "Search employees by partial name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "search_by_department",
        "description": "Search employees by department.",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string"
                }
            },
            "required": ["department"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "search_by_city",
        "description": "Search employees by city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "search_by_salary",
        "description": "Search employees within salary range.",
        "parameters": {
            "type": "object",
            "properties": {
                "minimum_salary": {
                    "type": "number"
                },
                "maximum_salary": {
                    "type": "number"
                }
            },
            "required": [
                "minimum_salary",
                "maximum_salary"
            ],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "count_employees",
        "description": "Count total employees.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "highest_salary",
        "description": "Find employee with highest salary.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "search_department_salary",
        "description":
            "Find employees in a department earning at least a salary.",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string"
                },
                "minimum_salary": {
                    "type": "number"
                }
            },
            "required": [
                "department",
                "minimum_salary"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
]


tool_functions = {

    "create_employee":
        create_employee,

    "get_employee":
        get_employee,

    "get_all_employees":
        get_all_employees,

    "update_employee":
        update_employee,

    "delete_employee":
        delete_employee,

    "search_by_name":
        search_by_name,

    "search_by_department":
        search_by_department,

    "search_by_city":
        search_by_city,

    "search_by_salary":
        search_by_salary,

    "count_employees":
        count_employees,

    "highest_salary":
        highest_salary,

    "search_department_salary":
        search_department_salary
}


def ask_agent(user_question):

    input_items = [

        {
            "role": "user",
            "content": user_question
        }

    ]

    while True:

        response = client.responses.create(

            model="gpt-5.6",

            instructions="""
            You are an AI employee database assistant.

            Use database tools whenever database
            information or database modification is requested.

            Never invent employee information.

            Before destructive operations such as DELETE,
            make sure the user's request clearly identifies
            the employee.

            Return a clear natural-language answer.
            """,

            tools=tools,

            input=input_items
        )

        input_items.extend(
            response.output
        )

        tool_called = False

        for item in response.output:

            if item.type == "function_call":

                tool_called = True

                function_name = item.name

                arguments = json.loads(
                    item.arguments
                )

                function = tool_functions[
                    function_name
                ]

                result = function(
                    **arguments
                )

                input_items.append(
                    {
                        "type":
                            "function_call_output",

                        "call_id":
                            item.call_id,

                        "output":
                            json.dumps(result)
                    }
                )

        if not tool_called:

            return response.output_text

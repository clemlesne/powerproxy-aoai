"""Script to test the proxy's ability to support response streaming when functions are used."""

# pylint: disable=line-too-long

import openai

openai.api_type = "azure"
openai.api_base = "http://localhost"
openai.api_version = "2023-07-01-preview"
openai.api_key = "123abc"

response = openai.ChatCompletion.create(
    engine="gpt",
    messages=[
        {
            "role": "user",
            "content": "Find beachfront hotels in San Diego for less than $300 a month with free breakfast.",
        }
    ],
    functions=[
        {
            "name": "search_hotels",
            "description": "Retrieves hotels from the search index based on the parameters provided",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location of the hotel (i.e. Seattle, WA)",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "The maximum price for the hotel",
                    },
                    "features": {
                        "type": "string",
                        "description": "A comma separated list of features (i.e. beachfront, free wifi, etc.)",
                    },
                },
                "required": ["location"],
            },
        }
    ],
    temperature=0,
    function_call="auto",
    stream=False,
)

print(response)

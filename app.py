from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import os
import base64

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get your OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"
PROMPT = """You are tasked with sorting waste based on an image of the item provided. Select the category that best fits the entire item or its individual components. If the item needs to be separated into different parts and disposed of in multiple categories, follow the format provided below.
1: Garbage
2: Recyclable
3: Compostable
4: Needles
5: E-Waste
6: Clothing

For example if the item is a tissue you would answer:
3: tissue

If the item must be split into multiple categories, provide the answer in this format: [number]: [item part], [number]: [item part], [number]: [item part]
For example, if an item consists of a coffee cup with a plastic lid, you would answer:
1: plastic lid, 2: paper cup

If there is no waste in the image return exactly:
7: Not applicable
"""


@app.route("/", methods=["GET", "POST"])
def handle_request():
    if request.method == "GET":
        return "Hello, World!"

    if request.method == "POST":
        # Get the image file from the request
        image = str(request.get_data())[2:-1]

        with open("out.txt", "w") as f:
            f.write(str(image))  # Convert the image content to string if necessary

        # Call the GPT API with the image
        response = gpt_with_image(image)

        # Return the response from the GPT API
        return jsonify(response), 200


def gpt_with_image(image):
    """
    Sends a request to OpenAI's GPT-4 model with the given image and prompt.
    """
    # Prepare headers for OpenAI API request
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Construct the payload for the GPT chat API with image support
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{image}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    # Send the request to OpenAI API
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    # print(1, response.text)
    responseJson = response.json()
    answer = responseJson["choices"][0]["message"]["content"]

    # Return the response as JSON
    if response.status_code == 200:
        return answer
    else:
        return {"error": response.json()}


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

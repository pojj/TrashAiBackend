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
PROMPT = """You will sort trash. Pick the option that best describes the image provided.
1: Garbage
2: Recyclable
3: Refundable
4: Compostable
5: Needles
6: E-Waste
7: Clothing
8: Put in Garbage, container in Compostable
9: Cap in Garbage, container in Recyclable
10: Utensils in Garbage, Napkin in Compostable, container in Garbage
11: Utensils in Garbage, Napkin in Compostable, container in Compostable
Return only the corresponding number.
"""


@app.route("/", methods=["GET", "POST"])
def handle_request():
    if request.method == "GET":
        return "Hello, World!"

    if request.method == "POST":
        # Check if the request contains the image and prompt data
        if "image" not in request.files:
            return jsonify({"error": "Image file is required"}), 400

        # Get the image file from the request
        image = request.files["image"]

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

    # Encode the image to base64
    base64_image = base64.b64encode(image.read()).decode("utf-8")

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
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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

    # Return the response as JSON
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

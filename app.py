import os

from flask import Flask, jsonify, request
from openai import AzureOpenAI

app = Flask(__name__)

client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)

DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT")


@app.route("/")
def home():
    return jsonify(
        {
            "status": "running",
            "message": "HR Copilot Agent is running",
        }
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    if not DEPLOYMENT_NAME:
        return jsonify({"error": "Azure OpenAI deployment is not configured."}), 500

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR Copilot assistant. "
                    "Answer employee questions clearly, professionally, and safely."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message.content

    return jsonify({"answer": answer})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

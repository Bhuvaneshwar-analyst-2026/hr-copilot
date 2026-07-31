import os

from flask import Flask, jsonify, request
from openai import AzureOpenAI

app = Flask(__name__)

DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT")


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Copilot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 700px;
                margin: 40px auto;
                padding: 20px;
            }

            textarea {
                width: 100%;
                height: 100px;
                padding: 10px;
            }

            button {
                margin-top: 10px;
                padding: 10px 18px;
                cursor: pointer;
            }

            #answer {
                margin-top: 20px;
                padding: 15px;
                background: #f4f4f4;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <h1>HR Copilot</h1>
        <p>Ask an HR-related question.</p>

        <textarea id="question" placeholder="Type your question here"></textarea>
        <br>
        <button onclick="askQuestion()">Ask</button>

        <div id="answer"></div>

        <script>
            async function askQuestion() {
                const question = document.getElementById("question").value;
                const answerBox = document.getElementById("answer");

                if (!question.trim()) {
                    answerBox.textContent = "Please enter a question.";
                    return;
                }

                answerBox.textContent = "Thinking...";

                try {
                    const response = await fetch("/chat", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ question: question })
                    });

                    const data = await response.json();

                    answerBox.textContent =
                        data.answer || data.error || "No response received.";
                } catch (error) {
                    answerBox.textContent = "Unable to contact HR Copilot.";
                }
            }
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key or not DEPLOYMENT_NAME:
        return jsonify(
            {
                "error": "Azure OpenAI is not configured yet.",
                "status": "configuration_required",
            }
        ), 503

    client = AzureOpenAI(
        api_key=api_key,
        api_version=os.environ.get(
            "AZURE_OPENAI_API_VERSION",
            "2024-02-01",
        ),
        azure_endpoint=endpoint,
    )

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an HR Copilot assistant. "
                        "Answer employee questions clearly, "
                        "professionally, and safely."
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

    except Exception as error:
        app.logger.exception("Azure OpenAI request failed")

        return jsonify(
            {
                "error": "The HR Copilot could not process the request.",
                "details": str(error),
            }
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

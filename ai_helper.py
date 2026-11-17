

import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def generate_ai_response(prompt):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("Groq API key not found in .env file.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are StudyMate AI, an expert student tutor. "
                    "Give accurate and student-friendly answers."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_completion_tokens=5000
    )

    return response.choices[0].message.content


def generate_quiz(topic, difficulty, number_questions):

    prompt = f"""
    Create exactly {number_questions} multiple-choice questions.

    Subject/topic: {topic}
    Difficulty: {difficulty}

    Return ONLY valid JSON. Do not use Markdown code fences.

    Use this exact structure:

    {{
      "questions": [
        {{
          "question": "Question text",
          "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D"
          ],
          "answer": "Option B",
          "explanation": "Explanation"
        }}
      ]
    }}

    Rules:
    - Exactly four options per question.
    - Only one correct answer.
    - The answer must exactly match one option.
    - Questions must be factually accurate.
    - Each question must be different.
    - Include a short explanation.
    - Do not reveal answers outside the JSON.
    """

    raw_response = generate_ai_response(prompt)

    # Extract JSON safely
    match = re.search(
        r"\{[\s\S]*\}",
        raw_response
    )

    if not match:
        raise ValueError("AI did not return valid quiz JSON.")

    data = json.loads(match.group())

    questions = data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("Invalid quiz format.")

    if len(questions) != number_questions:
        raise ValueError("AI returned an incorrect number of questions.")

    for question in questions:

        options = question.get("options")
        answer = question.get("answer")

        if (
            not isinstance(question.get("question"), str)
            or not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(option, str) for option in options)
            or not isinstance(answer, str)
            or answer not in options
            or not isinstance(question.get("explanation"), str)
        ):
            raise ValueError("AI generated an invalid question.")

    return questions

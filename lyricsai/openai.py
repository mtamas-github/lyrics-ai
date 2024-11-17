import openai
from decouple import config
import json

DEFAULT_LLM_MODEL = "gpt-4o"

class OpenAIAPI:
    def __init__(self):
        openai.api_key = config("OPENAI_API_KEY")
        self.client = openai.OpenAI(
            api_key=config("OPENAI_API_KEY")
        )
        self.summary = ""
        self.countries = []
        self.error = ""
        self.llm_model = config("OPENAI_LLM_MODEL", DEFAULT_LLM_MODEL)

    def analyze_lyrics(self, lyrics: str) -> None:
        """
        Sends song lyrics to the OpenAI API and returns a summary
        and a list of countries mentioned in the lyrics in JSON format.

        :param: lyrics The lyrics of the song to analyze.
        :return: A dictionary with the summary and list of countries.
        """
        chat_config = (
            f"Analyze the following song lyrics:\n\n{lyrics}\n\n"
            "Provide a JSON response with the following format:\n"
            "{\n"
            "  \"summary\": \"One-sentence summary of the song\",\n"
            "  \"countries\": [\"List of countries mentioned in the lyrics\"]\n"
            "}"
        )
        messages = [
            {
                "role": "system",
                "content": chat_config
            },
            {
                "role": "user",
                "content": lyrics
            }
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=64,
                response_format={"type": "json_object"}
            )
            print("original", response.choices)
            response_message = response.choices[0].message
            print("response_message", response_message)
            response_text = response_message.content
            result = json.loads(response_text)
        except json.JSONDecodeError:
            self.error = f"Failed to parse JSON response from OpenAI. response_text: {response_text}"
        except Exception as e:
            self.error = f"Generic error while called LLM model: {str(e)}"
        else:
            self.summary = result.get("summary", "")
            self.countries = result.get("countries", [])

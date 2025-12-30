from flask import Flask, request
from dotenv import load_dotenv
import os
from google import genai
from flask_cors import CORS
import pybase64

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

@app.route('/mnemonic', methods=['POST'])
def get_mnemonic():
    body = request.get_json()
    character = body.get('character')
    meaning = body.get('meaning')
    parts = body.get('parts')

    if not character or not meaning or not parts:
        print(request.json)
        return {"error": "Missing required parameters."}, 400

    prompt = f"I am learning the Japanese Kanji '{character}' which means '{meaning}'."
    prompt += f"I have visually broken it down into these parts/shapes: {parts}."
    prompt += f"Create a short, memorable, and vivid mnemonic story (max 1 sentence) that links these parts together to explain the meaning '{meaning}'."
    prompt += f"The tone should be helpful and slightly imaginative."

    response = client.models.generate_content(
      model="gemini-2.5-flash", contents=prompt
    )
    return response.text, 200
  
@app.route('/imagen', methods=['POST'])
def get_imagen():
  body = request.get_json()
  character = body.get('character')
  mnemonic = body.get('mnemonic')
  image = body.get('image')
  if not character or not mnemonic or not image:
      return {"error": "Missing required parameters."}, 400
  prompt = f"I have uploaded an image of the Kanji [{character}]."
  prompt += f"Modify this image by overlaying stylized depictions of its component parts directly over their corresponding positions in the character."
  prompt += f"You are making semi-transparent illustrations to overlay the original grey character. Do not replace the original illustration."
  prompt += f"Use a soft watercolor style for the overlays"
  prompt += f"Remove the labels. Align the new graphics perfectly with the character's structure."
  prompt += f"Maintain the positioning of the original character."
  prompt += f"Use the following mnemonic to guide the illustration: '{mnemonic}'."
  response = client.models.generate_content(
    model="gemini-2.5-flash-image", #gemini-3-pro-image-preview
    contents=[prompt, image]
  )
  
  response_image = None
  
  for part in response.parts:
    if part.inline_data is not None and part.inline_data.data is not None:
      raw_bytes = part.inline_data.data
      base64_string = pybase64.b64encode(raw_bytes).decode('utf-8')
      return {"image": base64_string}, 200

  return {"error": "No image generated."}, 500
  
if __name__ == '__main__':
    app.run(debug=True)
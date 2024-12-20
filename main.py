from fasthtml.common import *
import anthropic, os, base64, uvicorn
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles  # StaticFiles 추가

load_dotenv()


# antropic key 연결하고 초기 세팅부분
key = os.getenv('ANTHROPIC_API_KEY')

if not key:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")
client = anthropic.Anthropic(api_key=key)

app = FastHTML(hdrs=(picolink, Script("/canvas.js", type="module")))

@app.get("/")
def home():
    return Title('Drawing Demo'), Main(
        H1("내가 그린 그림으로 시 짓기"),
        Canvas(id="drawingCanvas", width="500", height="500",
               style="border: 1px solid black; background-color: #f0f0f0;"),
        Div("Draw something", id="caption"), cls='container')


@app.post("/process-canvas")
async def process_canvas(image: str):
    image_bytes = await image.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        temperature=0.5,
        messages=[
           {"role": "user",
            "content": [
                {"type": "image",
                "source": {"type": "base64","media_type": "image/png",
                "data": image_base64}},
                {"type": "text",
                 "text": "이 그림에 대한 시를 간단히 세줄로 적어줘"}
                #"text": "Write a haiku about this drawing, respond with only that."}
            ]}]
    )
    caption =  message.content[0].text.replace("\n", "<br>")
    return JSONResponse({"caption": caption})

serve()
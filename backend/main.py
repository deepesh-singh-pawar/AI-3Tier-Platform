from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import requests

DATABASE_URL = "postgresql://postgres:postgres@db:5432/chatdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    question = Column(String(500))
    answer = Column(Text)


Base.metadata.create_all(bind=engine)


app = FastAPI()

OLLAMA_URL = "http://ollama:11434/api/generate"


@app.get("/", response_class=HTMLResponse)
def home():
    db = SessionLocal()

    chats = db.query(Chat).all()

    html = """
    <!DOCTYPE html>
<html>
<head>
<title>AI Microservice Chat Platform</title>

<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 0;
}

.container {
    width: 60%;
    margin: auto;
    margin-top: 60px;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
}

h2 {
    text-align: center;
    color: #333;
}

form {
    display: flex;
    gap: 10px;
}

input {
    flex: 1;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-size: 16px;
}

button {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    background: #0056b3;
}

.history {
    margin-top: 30px;
}

.chat-box {
    background: #f1f3f5;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}
</style>

</head>

<body>

<div class="container">

<h2>🤖 Ask Ollama AI Assistant</h2>

<form method="post" action="/ask">
    <input name="prompt" placeholder="Type your question here..." required />
    <button type="submit">Send 🚀</button>
</form>

<div class="history">

<h3>📜 Chat History</h3>

{% for chat in chats %}
<div class="chat-box">
<b>👤 You:</b> {{ chat.question }} <br><br>
<b>🤖 AI:</b> {{ chat.answer }}
</div>
{% endfor %}

</div>

</div>

</body>
</html>
    """

    for chat in chats:
        html += f"<p><b>Q:</b> {chat.question}<br><b>A:</b> {chat.answer}</p>"

    return html


@app.post("/ask", response_class=HTMLResponse)
def ask(prompt: str = Form(...)):

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    answer = response.json()["response"]

    db = SessionLocal()

    chat = Chat(question=prompt, answer=answer)

    db.add(chat)
    db.commit()

    return f"""
    <h3>Response:</h3>
    <p>{answer}</p>
    <a href="/">Back</a>
    """
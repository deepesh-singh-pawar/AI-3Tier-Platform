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
    <h2>Ask Ollama</h2>

    <form method="post" action="/ask">
        <input name="prompt"/>
        <button type="submit">Send</button>
    </form>

    <hr>

    <h3>History</h3>
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
import os
import re
import requests
import fitz
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def extract_file_id(url):
    """Витягує ID файлу з посилання Google Drive."""
    pattern = r"/d/([a-zA-Z0-9_-]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Не вдалося знайти ID файлу в посиланні.")

def download_from_google_drive(file_id, destination):
    """Завантажує файл з Google Drive за ID."""
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = _get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    _save_response_content(response, destination)

def _get_confirm_token(response):
    """Отримує токен підтвердження для великих файлів."""
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def _save_response_content(response, destination):
    """Зберігає вміст відповіді у файл."""
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)


def read_file(file_path):
    """Читає текст із файлу (PDF або DOCX)."""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    if ext == '.pdf':
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    elif ext == '.docx':
        doc = Document(file_path)
        for element in doc.element.body:
            if isinstance(element, CT_P):
                para = element.xpath('.//w:t')
                para_text = ''.join([p.text for p in para if p.text])
                text += para_text.strip() + "\n"
            elif isinstance(element, CT_Tbl):
                table = element.xpath('.//w:tr')
                for row in table:
                    cells = row.xpath('.//w:tc')
                    row_text = "\t".join(["".join(cell.xpath('.//w:t/text()')) for cell in cells])
                    text += row_text.strip() + "\n"
    else:
        raise ValueError("Непідтримуваний тип файлу: " + ext)

    return text


def analyze_resume(file_url: str, freelancer_id: int):
    """Основна функція: завантажує файл за посиланням, читає його і надсилає у LLM."""
    file_id = extract_file_id(file_url)
    filename = f'downloaded_cv_{freelancer_id}.docx'
    download_from_google_drive(file_id, filename)

    resume_text = read_file(filename)

    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("OPEN_AI_BASE_URL")
    )

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL"),
        messages=[
            {"role": "system", "content": (
                "Ти експерт у складанні резюме. Твоя задача — уважно аналізувати резюме кандидата "
                "і надати чіткі, конструктивні рекомендації щодо його покращення українською мовою "
                "(структура, зміст, стиль, помилки тощо)."
            )},
            {"role": "user", "content": f"Ось текст резюме:\n\n{resume_text}"},
        ],
    )

    return response.choices[0].message.content



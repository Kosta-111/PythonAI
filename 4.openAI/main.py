import os
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import chromadb
from dotenv import load_dotenv

# Завантажити ключ
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. Зчитування PDF
def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 2. Розбиття на частини
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text)

# 3. Отримання embedding
def get_embedding(text):
    result = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return result.data[0].embedding

# 4. Створення ChromaDB та збереження
def build_vector_db(chunks):
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="book")

    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        collection.add(documents=[chunk], embeddings=[emb], ids=[str(i)])

    return collection

# 5. Пошук схожих частин
def retrieve_context(question, collection, top_k=3):
    query_emb = get_embedding(question)
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    return "\n".join(results["documents"][0])

# 6. Відповідь GPT
def ask_gpt(context, question):
    messages = [
        {"role": "system", "content": "Ти асистент, який відповідає на основі наданого контексту."},
        {"role": "user", "content": f"Контекст:\n{context}\n\nПитання: {question}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content

# === ОСНОВНИЙ СЦЕНАРІЙ ===
if __name__ == "__main__":
    # 1. Завантаж PDF
    text = load_pdf("book.pdf")
    print("✅ PDF завантажено")

    # 2. Розбий на частини
    chunks = split_text(text)
    print(f"✅ Розбито на {len(chunks)} частин")

    # 3. Побудуй базу знань
    collection = build_vector_db(chunks)
    print("✅ Векторну БД побудовано")

    # 4. Діалог
    while True:
        query = input("\n🧑 Ви: ")
        if query.lower() in ['вихід', 'exit', 'quit']:
            break

        context = retrieve_context(query, collection)
        answer = ask_gpt(context, query)
        print(f"\n🤖 Бот: {answer}")

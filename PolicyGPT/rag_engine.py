from pathlib import Path

import ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE = Path(__file__).parent
DATA = BASE / "data"
INDEX = BASE / ".index"
MODEL = "mistral"
MISSING = "Bu konu belgelerde geçmiyor."

# Belgelerin ekranda görünen adları
TITLES = {
    "ikametgah.pdf": "Yerleşim yeri belgesi",
    "sgk.pdf": "SGK işe giriş bildirgesi",
    "vatandaslik.pdf": "Vatandaşlık başvurusu",
    "vergi.pdf": "Vergi mükellefiyeti başvurusu",
}

PROMPT = """Aşağıda başlıklarıyla birlikte resmî belgeler var. Soruyu yalnızca bu belgelere dayanarak Türkçe cevapla.

İlk satıra cevabı aldığın belgenin başlığını şöyle yaz: KAYNAK: <başlık>
Sonra yalnızca uygulanabilir adımları kısa, numaralı bir liste olarak yaz (1., 2., 3. ...).
Giriş cümlesi, açıklama, yorum ya da parantez içinde not ekleme. Belgelerde olmayan bir adımı uydurma.
Soru bu belgelerden hiçbiriyle ilgili değilse yalnızca şunu yaz: KAYNAK: yok

Belgeler:
{context}

Soru: {question}
"""

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
_store = None


def _stamp():
    # The index is rebuilt only when a PDF is added, removed or changed
    return "\n".join(f"{p.name}:{p.stat().st_mtime_ns}" for p in sorted(DATA.glob("*.pdf")))


def _load_store():
    global _store
    if _store is not None:
        return _store

    stamp = _stamp()
    if (INDEX / "stamp").exists() and (INDEX / "stamp").read_text() == stamp:
        _store = FAISS.load_local(str(INDEX), embeddings, allow_dangerous_deserialization=True)
        return _store

    docs = []
    for path in sorted(DATA.glob("*.pdf")):
        docs.extend(PyPDFLoader(str(path)).load())
    if not docs:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    _store = FAISS.from_documents(splitter.split_documents(docs), embeddings)
    _store.save_local(str(INDEX))
    (INDEX / "stamp").write_text(stamp)
    return _store


def documents():
    return [{"file": p.name, "title": TITLES.get(p.name, p.stem)} for p in sorted(DATA.glob("*.pdf"))]


def _name(doc):
    return Path(doc.metadata.get("source", "")).name


def _fold(text):
    # Lower-case and drop Turkish letters, so "SGK REHBERİ" and "sgk" can be compared
    return text.translate(str.maketrans("İIıÇçĞğÖöŞşÜüÂâ", "iiiccggoossuuaa")).lower()


def query(question):
    store = _load_store()
    if store is None:
        return {"steps": [], "sources": [], "error": "Hiçbir PDF dosyası yüklenemedi."}

    hits = store.similarity_search(question, k=4)
    context = "\n\n".join(f"[{TITLES.get(_name(h), _name(h))}]\n{h.page_content}" for h in hits)
    reply = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
        options={"temperature": 0},
    )
    lines = [line.strip() for line in reply["message"]["content"].strip().splitlines()]

    # First line names the document the answer came from
    source_line = next((line for line in lines if line.upper().startswith("KAYNAK")), "")
    named = _fold(source_line.partition(":")[2])
    if not named.strip(" <>().") or named.strip(" <>().").startswith("yok"):
        return {"steps": [], "note": MISSING, "sources": []}

    # Only the numbered list; models like to add a closing remark after it
    steps = []
    for line in lines:
        head, _, rest = line.partition(". ")
        if head.isdigit() and rest:
            steps.append(rest.strip())
        elif steps and not line:
            break
    if not steps:
        return {"steps": [], "note": MISSING, "sources": []}

    source = None
    for h in hits:
        name = _name(h)
        if _fold(TITLES.get(name, name)) in named or Path(name).stem in named:
            source = h
            break
    source = source or hits[0]
    name = _name(source)
    return {
        "steps": steps,
        "note": "",
        "sources": [{"title": TITLES.get(name, name), "file": name, "page": source.metadata.get("page", 0) + 1}],
    }


def warm_up():
    _load_store()

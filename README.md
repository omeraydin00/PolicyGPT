<p align="center">
  <img src="./assets/header.svg" alt="PolicyGPT" width="100%" />
</p>

Answers questions about official procedures in Turkey with numbered steps, taken from the documents it is given.

Python · LangChain · FAISS · Ollama (Mistral) · Flask

<img alt="PolicyGPT answering how to get a residence certificate" src="screenshots/cevap.png" />

Ask how to get a residence certificate, register an employee with SGK, apply for citizenship or register for tax, and PolicyGPT answers with what to do, step by step, and shows which document the answer came from. It answers only from the documents: a question none of them covers, such as how to get a passport, gets "Bu konu belgelerde geçmiyor." instead of a guess.

The PDFs in `data/` are split into chunks, embedded with `all-MiniLM-L6-v2` and kept in a FAISS index on disk, rebuilt only when a PDF is added or changed. For each question the closest passages go to Mistral with their titles, and the model names the document it used. Mistral runs locally through Ollama, so no document or question leaves the computer.

The four PDFs in `data/` are short guides written for the project, one per topic, so the answers are only as complete and current as they are. Check anything important on the official portal.

## Running it

You need Python 3.10 or newer and [Ollama](https://ollama.com).

```bash
ollama pull mistral

git clone https://github.com/omeraydin00/PolicyGPT.git
cd PolicyGPT/PolicyGPT
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 and pick one of the example questions, or type your own. To add a topic, put its PDF in `data/` and give it a title in `TITLES` in `rag_engine.py`. The first question takes a little longer while the embedding model loads and the index is built.

Made for the Deep Learning course at Sakarya University.

# PolicyGPT

Turns long government documents into short, step-by-step answers.

Python · LangChain · FAISS · Ollama (Mistral) · Flask

<p>
  <img width="49%" alt="Residence certificate" src="https://github.com/user-attachments/assets/7c4fcef2-e3ef-4a86-937f-005e8d71da51" />
  <img width="49%" alt="Tax debt inquiry" src="https://github.com/user-attachments/assets/4302ce1d-e0ab-4044-84a7-9f391ccdc577" />
</p>

Official procedures in Turkey, such as registering a residence, getting a social security record, applying for citizenship or checking tax debt, are explained in long PDFs written in legal language. PolicyGPT reads those documents and answers a question with a numbered list of what to do, based on the documents rather than on the model's own guesses.

The PDFs in `data/` are split into overlapping chunks, embedded with `all-MiniLM-L6-v2` and stored in a FAISS index. For each question the closest passages are passed to Mistral, which runs locally through Ollama, so no document or question leaves the computer.

<p>
  <img width="49%" alt="Social security record" src="https://github.com/user-attachments/assets/e4b61ba5-73c1-482f-b1f3-b736248c31da" />
  <img width="49%" alt="Citizenship application" src="https://github.com/user-attachments/assets/dfefa890-048d-47a7-9787-e712c14c4ffc" />
</p>

## Running it

You need Python 3.10 or newer and [Ollama](https://ollama.com).

```bash
ollama pull mistral

git clone https://github.com/omeraydin00/PolicyGPT.git
cd PolicyGPT/PolicyGPT
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 and ask something like *"İkametgah belgesi nasıl alınır?"*. To add a topic, put its PDF in `data/` and add the path to `pdf_files` in `rag_engine.py`.

## Notes

- The index is rebuilt for every question; saving it to disk would make answers much faster.
- Answers are only as current as the PDFs. Check anything important on the official portal.

Made for the Deep Learning course at Sakarya University.

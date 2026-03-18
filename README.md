

# Service Ideas

## 1. Data Collection Pipilene for Product Authenticity

Pipeline for data collection based on user feedback to train image-based classfication of authenticity or imitation

# Computer Vision Deep Learning Solution Ideas

## 1. Administrative Document: Document AI / Intelligent Document Processing (IDP)

**OCR + document understanding + validation**

1. Extract text from documents (Registre de Commerce, NIF, etc.)
2. Understand the structure (fields like name, number, date…)
3. Validate / classify the document (is it legit? is it the right type?)

### A. OCR (Text extraction)

Use deep learning-based OCR instead of classical OCR.

**Options:**

- **EasyOCR**: good for quick start, supports Arabic + French
- **Tesseract**: older, less accurate
- **PaddleOCR**: very strong, especially for structured docs

For Algeria (French + Arabic mix): PaddleOCR

---

### B. Document Layout Understanding

A "Registre de Commerce" is structured:

- Titles
- Boxes
- Labels next to values

models that understand layout:

- **LayoutLM** (by Microsoft)
- **Donut (Document Understanding Transformer)**
- **LayoutLMv3** (best modern option)

These models take image + text + positions and output structured JSON like:

```json
{
  "company_name": "...",
  "rc_number": "...",
  "creation_date": "..."
}
```

---

### C. Field Extraction (NER for documents)

Once text is extracted, we can apply Named Entity Recognition (NER)

Example:

* "RC: 16/00-1234567 B 21" → rc_number
* "SARL XYZ" → company_name

Models:

* Fine-tuned BERT
* CamemBERT (good for French)
* Multilingual BERT

---

### D. Document Classification

We may receive:

* Registre de commerce
* Carte fiscale
* Other documents

And can train a classifier CNN or Vision Transformer (ViT) to classify documents

---

### E. Fraud / anomaly detection

We can detect:

* Fake documents
* Edited scans
* Missing fields

Techniques:

* Autoencoders (reconstruction error)
* CNN anomaly detection
* Rule-based + ML hybrid

---

### Challenges specific to Algeria

**Mixed language**

* French + Arabic
* Sometimes handwritten

**Low-quality scans**

* Photos from phones
* Shadows, blur

**No public datasets**

* Full automation is hard (impossible to reach 100%)
* Training data will be the biggest bottleneck
* Legal validation may still require human review

The goal is **AI-assisted verification**, not full automation

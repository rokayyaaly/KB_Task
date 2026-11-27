# RAG-Based Semester Course Advisor

A Retrieval-Augmented Generation system that recommends the courses a student should register for next semester, checks every recommendation against explicit Python rules, and shows the retrieved evidence behind each decision. A chatbot front-end lets students register conversationally.

> **All data is fictional.** "Nile Valley University (NVU)" and its catalog, rules and degree plan were written for this assignment. No official documents were used.

**Team:** Rokayya Aly (23010050) · Mohamed Elbassat (23010047)

## Folder structure
```
RAG_Course_Advisor.ipynb      main notebook (code + executed outputs)
see_retrieval.py              quick terminal demo (retrieval + citations for S002)
requirements.txt
kb/                           knowledge base (fictional)
  course_catalog.md             32 courses: credits, level, offering, prerequisites, corequisites, schedule, workload, description
  registration_rules.md         14 rules (R1–R14) with machine-readable parameters
  degree_plan.md                program structure, tracks, advising notes
data/student_profiles.json    6 synthetic student profiles (test inputs)
outputs/                      generated sample inputs/outputs
  profile_S00X_input.json / _output.json / _report.txt   (one set per profile)
  all_profiles_report.txt, summary.csv, chatbot_transcript.json
report/Report.md              project report
```

## Run
```bash
pip install -r requirements.txt        # numpy + scikit-learn are enough; sentence-transformers is optional
jupyter notebook RAG_Course_Advisor.ipynb   # then: Run All
```
Keep `kb/` and `data/` in the same folder as the notebook. Google Colab: upload the three folders/files, run `!pip install -r requirements.txt`, then Run All.

* **Embeddings:** the notebook uses `sentence-transformers/all-MiniLM-L6-v2` if installed, otherwise a TF-IDF (unigram + bigram) fallback with L2-normalised cosine similarity. Rule decisions do not depend on the embedder.
* **LLM (optional, recommended):** set a free **`NVIDIA_API_KEY`** from [build.nvidia.com/settings](https://build.nvidia.com/settings) before starting Jupyter. The notebook calls NVIDIA NIM (`nvidia/nemotron-3.5-bolt-e4b` by default; override with `NVIDIA_MODEL`) over the OpenAI-compatible endpoint. You can also set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. Without a key an evidence-grounded template is used, so the notebook runs fully offline.
* **Chat interactively:** uncomment `chat_cli()` in section 9.

## How to test

### 1. Quick retrieval + citation demo (terminal)
Shows what RAG retrieved for student **S002**, the accepted schedule with `[refs: course_catalog.md#…]` on every reason, and excluded courses with rule evidence ranks.

**PowerShell:**
```powershell
cd "C:\Users\Legion 5\Desktop\KB_Task"
$env:NVIDIA_API_KEY = "nvapi-..."          # optional; omit for offline template
$env:NVIDIA_MODEL = "nvidia/nemotron-3.5-bolt-e4b"
python see_retrieval.py
```

**bash:**
```bash
cd /path/to/KB_Task
export NVIDIA_API_KEY="nvapi-..."          # optional
export NVIDIA_MODEL="nvidia/nemotron-3.5-bolt-e4b"
python see_retrieval.py
```

What to check in the output:
* **Retrieved course passages** list real sources like `course_catalog.md#MATH201`
* **Accepted reasons** end with `[refs: course_catalog.md#CODE (sim …); rules R…]`
* **Excluded courses** show `registration_rules.md#R…` with `retrieved_rank=1`
* **Rule audit** is `PASSED`

### 2. Saved sample outputs (no re-run needed)
```powershell
Get-Content .\outputs\profile_S002_report.txt
Get-Content .\outputs\summary.csv
Get-Content .\outputs\chatbot_transcript.json
```
Or open any `outputs/profile_S00X_report.txt` — each report has input → retrieved evidence → accepted (with sources) → excluded (with rule evidence) → audit.

### 3. Full notebook (all 6 profiles + chatbot)
1. Set `NVIDIA_API_KEY` (optional) as above.
2. Open `RAG_Course_Advisor.ipynb` → **Run All**.
3. Section 8 prints all six profiles; section 9 runs the scripted chatbot; section 10 refreshes `outputs/`.

Profiles to spot-check:
| ID | What it tests |
|---|---|
| S002 | Unmet prerequisites (AI301 blocked) + retrieval for ML/data science |
| S003 | Credit overload capped at 18 |
| S005 | Probation 12-credit cap |
| S006 | Timetable conflicts + incomplete catalog (CS499 flagged) |

### 4. Interactive chatbot
In the notebook, uncomment `chat_cli()` at the end of section 9, run that cell, and ask things like “why can't I take AI301?” or “what is the maximum number of credits?” — answers should cite `registration_rules.md#…` / catalog sources.

## Use your own student
Add an object to `data/student_profiles.json` (fields: `academic_year`, `semester`, `gpa` (or `null`), `completed` as `{code: grade}`, `other_credits`, `skills`, `interests`, `goals`, `desired_credits`, `workload_pref`, `requested_courses`) and re-run section 8. Changing numbers in `kb/registration_rules.md` (e.g. `max_credits=18`) changes the rule engine without touching code.

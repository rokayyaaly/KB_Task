---
title: "RAG-Based Semester Course Advisor — Project Report"
subtitle: "KBA Assignment · Team of 2 · Deadline 28/11/2026"
---

**Team members:** Rokayya Aly (23010050) · Mohamed Elbassat (23010047)

# 1. Aim and overview

The goal is a Python Retrieval-Augmented Generation (RAG) system that recommends which courses a student should register for in the coming semester. Each recommendation has to respect the student's knowledge (completed courses and grades), academic level, interests, preferred workload and the college's registration rules, and has to be backed by retrieved evidence rather than guesses.

The system we built has five parts, all in one notebook (`RAG_Course_Advisor.ipynb`):

1. A **knowledge base** of course descriptions, registration rules and a degree plan.
2. A **RAG pipeline** that parses and chunks the documents, embeds them, retrieves relevant passages and generates personalised explanations.
3. An explicit **Python rule engine** that blocks or flags any course that violates a documented rule.
4. A **recommendation builder** that ranks eligible courses and assembles a feasible schedule, then independently re-validates it.
5. A **chatbot** that collects the student's details in conversation and answers eligibility and policy questions.

# 2. Data sources

No official university documents were used. We wrote a **fictional** university, "Nile Valley University (NVU), BSc Computer Science & AI", and labelled every file as fictional. The three Markdown files in `kb/` are:

| File | Content |
|---|---|
| `course_catalog.md` | 32 courses (levels 100–400): credits, level, semester offering, prerequisites, corequisites, minimum earned credits, weekly schedule, category, workload (Light/Medium/Heavy), description and topics. One course (CS499) is deliberately incomplete to test missing-information handling. |
| `registration_rules.md` | 14 rules (R1–R14). Each has a machine-readable `Parameters` line (for example `max_credits=18`) and a plain-language `Text` line. |
| `degree_plan.md` | Program structure, core sequence by year, three specialisation tracks (AI, Software Engineering, Systems/Cloud/Security), workload and capstone advice. |

The test students are **synthetic** (`data/student_profiles.json`).

# 3. Approach

## 3.1 Parsing and chunking
The catalog and rules are parsed into structured Python records (dataclasses `Course`, `Rule`) with regular expressions. Fields such as "Not published" or "TBA" become `None` and the field name is added to the course's `missing` list. The same documents are turned into 54 text chunks: one per course, one per rule and one per degree-plan subsection. A sentence-aware splitter with overlap handles passages longer than 900 characters. Every chunk keeps its source reference, for example `course_catalog.md#AI301` or `registration_rules.md#R4`.

## 3.2 Embeddings and retrieval
Chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2` when it is installed. Otherwise the system falls back to scikit-learn TF-IDF with unigrams and bigrams, so it runs without downloads. In both cases vectors are L2-normalised and retrieval is cosine similarity over a NumPy matrix, restricted by chunk type when needed.

Retrieval is used twice:

* **Course and plan retrieval.** The query is built from the student's interests, goals and skills. The similarity score of each course is its *relevance* in the ranking, and the top degree-plan passages are shown as guidance.
* **Policy retrieval.** For every rule finding (a block, flag or credit-load note) the system queries the rule chunks with the finding text and reports where the applicable rule ranked. In all 49 findings across the six profiles the correct rule was retrieved at rank 1.

## 3.3 Rule engine
The checks are plain Python functions (`check_course`, `credit_policy`, `validate_plan`). Numeric parameters are read from the rules file, so editing the policy changes the behaviour. Each finding is **BLOCK** (violation, never recommended), **FLAG** (needs advisor approval or information is missing, never recommended automatically) or **INFO**. Where a detail is missing the system flags it and does not guess: a course with unpublished prerequisites, schedule or offering is flagged under R12, and a missing GPA means the GPA-dependent rules are reported as "not checkable".

## 3.4 Ranking and schedule building
Eligible courses are scored as

`score = 0.60 × relevance + 0.25 × program priority + 0.10 × workload fit + 0.05 × explicitly requested`

where relevance is the retrieval similarity normalised by the best eligible course, program priority rewards core courses due at or before the student's year (and required general education), and workload fit compares the course label with the student's preference. A greedy builder adds courses in score order under the credit limit (R1–R3), timetable (R9), corequisite (R10) and heavy-course (R13) rules; a course with an unmet corequisite is added together with its corequisite when both fit. The final list is then re-checked by `validate_plan()`, a separate function that re-applies every rule to the finished schedule. All six schedules passed this audit.

## 3.5 LLM and guardrail
`call_llm()` prefers the **free NVIDIA NIM** API (`NVIDIA_API_KEY` → `https://integrate.api.nvidia.com/v1/chat/completions`, default model `nvidia/nemotron-3.5-bolt-e4b`). It also accepts OpenAI or Anthropic keys. Calls use plain HTTPS (no SDK). The LLM receives only the retrieved catalog passages, degree-plan hits, matched interests and rule results, and writes one short reason per accepted course. A guardrail rejects the output if any recommended course is missing or any course code outside the catalog is mentioned, and then the deterministic template is used. After wording is set, the system **appends deterministic citations** of the form `[refs: course_catalog.md#CODE (sim …); rules R…]` from the retrieval/rule evidence — so source references are never invented by the LLM. The recommended course list itself is never decided by the LLM. Without an API key the template produces the reasons, so the system runs fully offline.

## 3.6 Chatbot
`AdvisorChatbot` fills the profile "slots" (year, semester, GPA, completed courses with grades, interests, goals, credits, workload) from free text, using an LLM JSON extractor when a key is set and regular expressions otherwise. It asks for missing details instead of inventing them (for example a course without a grade is assumed to be "C" and flagged; GPA or goals can be skipped). It handles four intents: recommend a schedule, explain why a course is not allowed (rule engine plus retrieved policy text), describe a course, and answer policy questions with retrieval. If the student changes a preference the plan is recomputed. A scripted conversation is in the notebook and saved in `outputs/chatbot_transcript.json`.

# 4. Rules enforced

| Rule | Policy | Enforcement |
|---|---|---|
| R1 | Standard load 12–18 credits; below 12 is part-time | Cap in `credit_policy`; part-time flag |
| R2 | GPA ≥ 3.5 may request up to 21 credits (advisor approval) | Raises limit, flags overload |
| R3 | GPA < 2.0 (probation): at most 12 credits | Caps the load |
| R4 | Prerequisites completed with grade C or better | Blocks missing or low-grade prerequisites |
| R5 | No repeat of courses passed with C or better; D/F may be retaken | Blocks repeats, allows retakes |
| R6 | Course level ≤ year × 100; one level above needs approval | Blocks two levels up, flags one level up |
| R7 | Academic year from earned credits (30/60/90) | Flags mismatch with stated year |
| R8 | Course must be offered in the semester | Blocks otherwise |
| R9 | No overlapping meeting times | Schedule builder + final audit |
| R10 | Corequisites completed or taken together | Bundles or blocks |
| R11 | Minimum earned credits (capstone: 90) | Blocks otherwise |
| R12 | Missing catalog information | Flags; never recommends automatically |
| R13 | At most 2 Heavy courses (1 if GPA < 2.5; 1 if GPA missing) | Schedule builder + final audit; FLAG when GPA missing |
| R14 | Advisor-approval process | Referred to in flag messages |

# 5. Test profiles and results

Six synthetic students were run. Full inputs, retrieved evidence, accepted and rejected courses and reasons are in `outputs/` and in the notebook.

| ID | Student | Year / term | GPA | Requested → limit | Result | Accepted courses | What it demonstrates |
|---|---|---|---|---|---|---|---|
| S001 | Sara | 1 / Fall | none | 15 → 18 | 15 cr | CS102, CS101, MATH101, PHYS101, ENG101 | New student, missing GPA flagged (R2/R3/R13 not fully checkable); AI301 blocked (prerequisites, level) |
| S002 | Omar | 2 / Spring | 3.1 | 15 → 18 | 14 cr | MATH201, STAT201, CS210, CS203, HUM201 | **Unmet prerequisite** (AI301 needs STAT201, MATH201) |
| S003 | Lina | 3 / Fall | 3.2 | 21 → 18 | 18 cr | CS370, CS301, CS320, CS310, CS340, AI320 | **Credit limit exceeded**: 21 requested, overload needs GPA 3.5; AI401 flagged (level); corequisite bundle CS370 + CS301 |
| S004 | Karim | 4 / Fall | 3.6 | 21 → 21 | 15 cr | CS401, CS410, SEC301, CS340, AI320 | Capstone with 98 earned credits; heavy-course limit excludes AI401 and CS370; CS411 blocked (needs CS410, offered in Spring only) |
| S005 | Nour | 2 / Fall | 1.8 | 18 → 12 | 12 cr | CS220, CS202, MATH101, CS201 | **Probation cap** of 12; MATH101 passed with D does not satisfy MATH201; retake of MATH101 allowed; one Heavy course maximum |
| S006 | Maya | 3 / Spring | 3.4 | 15 → 18 | 15 cr | AI310, CS330, CS310, AI320, CS350 | **Timetable conflicts** (CS302 vs CS330, CS340 vs AI310); AI402/AI403 flagged (level); CS499 flagged (missing catalog data) |

# 6. Sample result (S002, Omar Hassan)

**Input.** Year 2, Spring, GPA 3.1, 32 earned credits. Completed CS101 (A), CS102 (A-), MATH101 (B+), ENG101 (B), PHYS101 (B), CS201 (B+). Interests: machine learning, data science, Python. Wants 15 credits, medium workload, and asks for AI301.

**Retrieved evidence.** The top retrieved course passages are MATH201 (0.275), AI301 (0.266), AI320 and STAT201 (0.219 each). The top degree-plan passage is the *Artificial Intelligence track* (0.271), which describes MATH201 and STAT201 in Year 2 as the foundation for AI301.

**Accepted (14 credits, rule audit passed).**

| Course | Reason (generated from retrieved passage and rule results) | Sources |
|---|---|---|
| MATH201 Linear Algebra, 3 cr | Matches machine learning and data science; core Year 2 course; MATH101 (B+) satisfies the prerequisite | `course_catalog.md#MATH201`, R4, R6, R8, R9 |
| STAT201 Probability and Statistics, 3 cr | Matches machine learning and data science; core Year 2; MATH101 (B+) satisfies the prerequisite | `course_catalog.md#STAT201`, R4, R6, R8, R9 |
| CS210 Database Systems, 3 cr | Matches data science; core Year 2; CS201 (B+) satisfies the prerequisite | `course_catalog.md#CS210`, R4, R6, R8, R9 |
| CS203 Computer Organization, 3 cr | Core Year 2 course; CS101 (A) satisfies the prerequisite | `course_catalog.md#CS203`, R4, R6, R8, R9 |
| HUM201 Ethics and Society in Computing, 2 cr | Required general-education course; no prerequisites | `course_catalog.md#HUM201`, R4, R6, R8, R9 |

**Excluded.** AI301 Machine Learning Fundamentals is blocked by R4 (prerequisites STAT201 and MATH201 not completed) and also falls under R6 (level 300 is one level above Year 2), with the matching policy passages retrieved at rank 1. AI320 is blocked because STAT201 has not been completed. The system points out the way forward: completing STAT201 and MATH201 this semester makes AI301 available next semester. The plan is 14 of the 15 requested credits because no further eligible course fits the target without exceeding it.

# 7. Key limitations

* **Fictional, simplified data.** The catalog is small (32 courses) with one section per course. Real catalogs have multiple sections, seat limits, instructors, "or" prerequisites and exceptions.
* **Rules are encoded by hand.** The numeric parameters come from the policy file, but the logic of each rule is written in Python. A new kind of rule needs new code, and the system cannot read an arbitrary official policy PDF and turn it into checks automatically.
* **Retrieval quality depends on the embedder.** TF-IDF matches words rather than meaning (for example it ignores synonyms); vectors are L2-normalised so scores are cosine similarity. Sentence-transformer embeddings improve semantics when installed. Some low-similarity "filler" courses (core or general education) are chosen by program priority rather than relevance, and their reasons say so.
* **Greedy scheduling.** The builder is not guaranteed to find the best possible combination; for example a lower-ranked course can be dropped because a higher-ranked one overlaps with it.
* **LLM depends on a free NVIDIA key (or OpenAI/Anthropic).** Sample explanations were generated with NVIDIA NIM (`nvidia/nemotron-3.5-bolt-e4b`); without a key the offline template is used. The guardrail checks course codes only, not every factual statement.
* **Chatbot parsing is rule-based without an API key.** Regular-expression extraction handles common phrasings but not arbitrary language, and it may miss details.
* **Advisor decisions are out of scope.** Courses needing approval are flagged and kept out of the schedule; the system does not model the approval workflow, and it does not predict grades or workload for an individual student.

# 8. Conclusion

The system produces feasible, rule-compliant semester plans in which every accepted or rejected course is tied to a retrieved catalog or policy passage, explicit Python checks prevent violations, and missing information is flagged instead of guessed. The architecture separates *what is allowed* (rule engine), *what is relevant* (retrieval) and *how it is explained* (LLM or template), which keeps the recommendations auditable.

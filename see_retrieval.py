"""
Quick demo: show retrieval hits + cited reasons for one student.
Usage (PowerShell):
  cd "C:\\Users\\Legion 5\\Desktop\\KB_Task"
  $env:NVIDIA_API_KEY = "nvapi-..."   # optional; works offline without it
  $env:NVIDIA_MODEL = "nvidia/nemotron-3.5-bolt-e4b"
  python see_retrieval.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

# Execute notebook code cells to load the advisor
nb = json.loads((ROOT / "RAG_Course_Advisor.ipynb").read_text(encoding="utf-8"))
ns = {"__name__": "__main__"}
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell.get("source", []))
    # Stop before the mass profile run / chatbot demo / save cells
    if i >= 16:
        break
    # Still need recommend+explain (cell 14) and format helpers aren't required
    try:
        exec(compile(src, f"cell_{i}", "exec"), ns)
    except Exception as e:
        print(f"Failed on cell {i}: {type(e).__name__}: {e}")
        sys.exit(1)

profiles = ns["load_profiles"](ns["DATA_DIR"] / "student_profiles.json")
s = next(p for p in profiles if p.student_id == "S002")
print("=" * 78)
print(f"STUDENT {s.student_id} – {s.name} | Year {s.academic_year} {s.semester} | GPA {s.gpa}")
print(f"Interests: {', '.join(s.interests)}")
print(f"Goals: {s.goals}")
print(f"LLM: {ns.get('LLM_PROVIDER') or 'offline template'}")
print("=" * 78)

result = ns["recommend"](s)

print("\n1) RETRIEVED course passages (what the RAG found):")
for t in result["retrieval"]["top_courses"]:
    print(f"   #{t['rank']}  {t['code']:7}  sim={t['score']:.3f}  [{t['source']}]")

print("\n2) RETRIEVED degree-plan passages:")
for p in result["retrieval"]["degree_plan_passages"]:
    print(f"   sim={p['score']:.3f}  [{p['source']}]")
    print(f"      {p['text'][:140].replace(chr(10), ' ')}...")

print("\n3) ACCEPTED courses — LLM/template reason + deterministic refs:")
for a in result["accepted"]:
    print(f"   • {a['code']} {a['title']} ({a['credits']} cr)")
    print(f"     {a['reason']}")

print("\n4) EXCLUDED (with retrieved rule evidence):")
for e in result["excluded"][:4]:
    print(f"   ✘ {e['code']} [{e['status']}]")
    for r in e["reasons"][:2]:
        ev = r["evidence"]
        print(f"       [{r['rule']}] {r['message']}")
        print(f"       evidence [{ev['source']}] retrieved_rank={ev['retrieved_rank']} sim={ev['retrieval_score']}")

print("\n5) Explanation mode:", result["explanation_mode"])
print("   Rule audit:", "PASSED" if result["validation"]["passed"] else result["validation"]["violations"])
print("\nDone. Every accepted reason should end with [refs: course_catalog.md#...].")

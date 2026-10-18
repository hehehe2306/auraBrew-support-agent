"""單元 4 第六章：自己寫 RAG 的檢索半邊（第 1–3、6 步），對課程列表跑 K1–K10。

只做檢索，不呼叫生成模型，不需要任何 API key。
用法：python experiments/rag_retrieval.py [--model BAAI/bge-m3] [--split unit|h3]
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

KB = Path(__file__).resolve().parent.parent / "knowledge" / "ai_agent_course_syllabus.md"

# 題目取自 docs/drafts/第五週學習文件_單元4.md 的測試集；expect 是預期該撈到的單元（None＝列表沒有）
QUESTIONS = [
    ("K1", "單元 4 的實踐要做什麼？", [4]),
    ("K2", "哪一個單元在教 Guardrail？", [8]),
    ("K3", "哪些單元的實踐要求要用到 chatflow？", [6, 7, 8]),
    ("K4", "單元 11 在教什麼？", None),
    ("K5", "期末專題什麼時候要交？", None),
    ("K6", "怎麼避免使用者用話術讓 AI 失控？", [2, 8]),
    ("K6b", "怎麼防止 prompt injection？", [2, 8]),
    ("K7", "「intent recognition」在哪個單元？", [6]),
    ("K8", "單元 0 的內容介紹叫我怎麼辦？", [0]),
    ("K9", "單元 1 要我找出哪個模型？", [1]),
    ("K10", "老師的認知欄位對單元 1 說了什麼？", [1]),
]


def chunk(text, split):
    """step 1：切割。unit＝每個 `## 單元 N` 一段；h3＝再依 `###` 切（標題帶單元名）。"""
    parts = re.split(r"(?m)^(?=## )", text)
    chunks = []
    for p in parts:
        m = re.match(r"## 單元 (\d+)", p)
        unit = int(m.group(1)) if m else None
        if split == "unit":
            chunks.append((unit, p.strip()))
        else:
            head = p.splitlines()[0] if m else ""
            subs = re.split(r"(?m)^(?=### )", p)
            for s in subs:
                s = s.strip()
                if s and s != head:
                    chunks.append((unit, (head + "\n" + s) if m and not s.startswith(head) else s))
    return [(u, c) for u, c in chunks if c]


def label(u):
    return "頭" if u is None else str(u)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-m3")
    ap.add_argument("--split", choices=["unit", "h3"], default="unit")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    chunks = chunk(KB.read_text(encoding="utf-8"), a.split)
    model = SentenceTransformer(a.model)
    # step 2：每段轉向量（正規化後 cosine＝內積）
    doc_vecs = model.encode([c for _, c in chunks], normalize_embeddings=True)
    print(f"model={a.model} split={a.split} chunks={len(chunks)} max_seq={model.max_seq_length}")
    print("chunk 字數:", [(label(u), len(c)) for u, c in chunks])

    results = []
    for qid, q, expect in QUESTIONS:
        qv = model.encode([q], normalize_embeddings=True)[0]
        scores = doc_vecs @ qv  # step 3：cosine
        order = np.argsort(-scores)
        top = [(label(chunks[i][0]), round(float(scores[i]), 3)) for i in order[: a.k]]
        # 預期單元在全部排名中的名次（同單元多段取最佳）
        ranks = {}
        if expect:
            for e in expect:
                r = next(n for n, i in enumerate(order, 1) if chunks[i][0] == e)
                ranks[e] = (r, round(float(scores[order[r - 1]]), 3))
        results.append({"id": qid, "q": q, "expect": expect, "top": top, "expect_rank": ranks})
        print(f"\n{qid} {q}  預期={expect}")
        print("  top:", top)
        if ranks:
            print("  預期單元(名次,分數):", ranks)  # step 6：記錄分數
    if a.out:
        Path(a.out).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

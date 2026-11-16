# 單元 7 訪談 Chatflow：節點設定與 Prompt 備份

老師說 Coze 要下架。這份把 Coze 裡「只存在平台上」的東西（三個 LLM 的 Prompt、Code 節點程式、各節點設定）存成文字，萬一平台消失還能照著重建，也能搬到自己的程式。流程的設計理由與測試結果見 `docs/drafts/第八週學習文件_單元7.md`，設計與實際的差異見 `docs/drafts/單元7_節點設計.md`。

**這份備份的可信度（先講清楚）：**

- 下面的 Prompt 與程式，是我當初輸入進 Coze 的文字，從對話紀錄抄下來，**沒有事後從 Coze 讀回來逐字比對**。
- 行為有驗證：用這套設定跑過 5 次對話輸入（M0、B、A、C），Code 節點的輸入輸出和回覆都符合預期。
- 沒驗證的：Code 編輯器是 Monaco，輸入時可能有自動補全；程式跑得正確，但我沒有把儲存的原文和下面這份做字元級比對。
- Knowledge retrieval 的「最大召回」與「最小匹配度」用的是預設值，我沒記下數字。

## 位置與名稱

- Coze App：`單元7_訪談Chatflow`；Chatflow：`course_interview_chatflow`（建立時勾選「綁定同名對話」）。
- 要 Test run 必須先在 Role configurations 填 Role name：`course_assistant`。
- 模型：三個 LLM 節點都是 GPT-4o。

## 變數（Variables → User variable，4 個，皆為字串、無預設值）

`gender`、`occupation`、`age`、`course`

為什麼是 User variable：App variable 的說明是「每次新請求都初始化成預設值」，User variable 才是「持續儲存」（依設定頁說明文字；實測 User variable 跨輪、隔天仍在）。

## 流程連線

```
Start → LLM（抽取）→ Code（合併）→ Variable assign → Condition
   If（Code.missing is empty）→ Knowledge retrieval → LLM_1（回應）→ End
   Else                       → LLM_2（追問）                      → End
```

## 1. LLM（抽取）

- 輸入：`input` ← Start 的 `USER_INPUT`
- 輸出格式：JSON；輸出變數（皆 String）：`gender`、`occupation`、`age`、`course`

System Prompt：

```
You extract user profile fields from the user's latest message. Fill gender, occupation, age and course ONLY if the message explicitly says them; otherwise return an empty string for that field. Never guess or invent values. age is a string such as 22. course is the course the user wants to take. Return only the four fields.
```

User Prompt：

```
{{input}}
```

## 2. Code（合併）— JavaScript

輸入（8 個，皆字串）：

| 變數 | 來源 |
| :- | :- |
| `n_gender` / `n_occupation` / `n_age` / `n_course` | 抽取 LLM 的 `gender` / `occupation` / `age` / `course`（本輪新抽到的） |
| `o_gender` / `o_occupation` / `o_age` / `o_course` | User variable 的 `gender` / `occupation` / `age` / `course`（記住的舊值） |

輸出（5 個，皆 String）：`gender`、`occupation`、`age`、`course`、`missing`

我輸入的程式（單行，因為編輯器自動縮排會把多行貼上弄亂）：

```js
async function main({ params }: Args): Promise<Output> { const pick = (n, o) => (n && String(n).trim() !== "") ? String(n).trim() : (o || ""); const gender = pick(params.n_gender, params.o_gender); const occupation = pick(params.n_occupation, params.o_occupation); const age = pick(params.n_age, params.o_age); const course = pick(params.n_course, params.o_course); const missing = [["gender", gender], ["occupation", occupation], ["age", age], ["course", course]].filter(x => x[1] === "").map(x => x[0]).join(","); return { gender, occupation, age, course, missing }; }
```

等價的展開寫法與規則：本輪非空就覆蓋舊值，否則保留舊值；`missing` 是仍為空的欄位名稱以逗號串起（四欄都齊則為空字串）。

```js
const pick = (n, o) => (n && String(n).trim() !== "") ? String(n).trim() : (o || "");
const gender = pick(params.n_gender, params.o_gender);
// occupation / age / course 同理
const missing = [["gender", gender], ["occupation", occupation], ["age", age], ["course", course]]
  .filter(x => x[1] === "").map(x => x[0]).join(",");
return { gender, occupation, age, course, missing };
```

## 3. Variable assign

四列，把合併結果寫回 User variable：`gender` ← Code.`gender`、`occupation` ← Code.`occupation`、`age` ← Code.`age`、`course` ← Code.`course`。

## 4. Condition

- If：`Code.missing` **is empty**（運算子選「is empty」）→ 走知識庫。
- Else → 走追問。

## 5. Knowledge retrieval

- Query ← Code.`course`
- 知識庫：`course_syllabus`（上傳 `knowledge/ai_agent_course_syllabus.md`；Text format、Local documents；Quick Parsing、Automatic segmentation & Cleaning；匯入後 1 份文件 8 個片段）
- 搜尋策略 Hybrid；最大召回、最小匹配度用預設；**Query Rewriting 關閉**
- 注意：這個節點**預設會帶最近 3 輪對話歷史**（執行紀錄顯示 `enableChatHistory=true`、`chatHistoryRound=3`），我沒有改。測試 C 時它對「烘焙課」並沒有回空（撈到 2 個片段），所以實際查詢可能受前面對話影響。

## 6. LLM_1（回應）

- 輸入：`kb` ← Knowledge retrieval 的 `outputList`（陣列）；`course` ← Code.`course`
- 輸出格式：Text；輸出變數 `output`

System Prompt：

```
You are a course assistant. Answer the user's question about the wanted course using ONLY the retrieved syllabus content provided. If the retrieved content does not mention the course, say clearly that the syllabus has no information about it. Never invent course details. Reply in Traditional Chinese, briefly.
```

User Prompt：

```
Wanted course: {{course}} Retrieved syllabus content: {{kb}}
```

## 7. LLM_2（追問）

- 輸入：`missing` ← Code.`missing`
- 輸出格式：Text；輸出變數 `output`

System Prompt：

```
You are a friendly course assistant interviewing a user. Some profile fields are still missing. Ask the user for ONLY ONE of the missing fields, politely and briefly, in Traditional Chinese. The fields are gender, occupation, age, and wanted course. Do not ask for fields that are not in the missing list. Do not answer course questions yet.
```

User Prompt：

```
Missing fields (comma separated): {{missing}}
```

## 8. End

- 回傳方式：Return text
- 輸出變數：`output` ← LLM_1.`output`；`ask` ← LLM_2.`output`
- Response 模板：`{{output}}{{ask}}`（兩條分支互斥，只會有一個有值）

## 換到自己的程式時，這些怎麼對應（推論，沒有實作）

- 三個 LLM 節點 → 三次模型呼叫；兩個 Prompt（抽取、追問／回應）原樣可用。
- Code 合併 → 一個普通函式，可直接寫單元測試（輸入「舊狀態 + 本輪抽取」）。
- User variable → 一個 dict／JSON 檔（或資料庫）。
- Condition → `if missing == ""`。
- Knowledge retrieval → 自己的檢索函式（可參考 `experiments/rag_retrieval.py`）。

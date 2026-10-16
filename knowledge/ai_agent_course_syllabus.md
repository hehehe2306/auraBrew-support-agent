# 115-1 中央大學 AI Agent 課程列表(Knowledge 用)

> 來源:老師提供的「115-1_中央大學AI-Agent課綱.xlsx」第一個工作表,每個單元一段,欄位照原表,文字未改寫。上傳到 Coze 的 Knowledge 用。

## 單元 0：拖拉式 AI Agent 導論與 Coze 平台初探/用 AI IDE 編寫你的進度報告，並上傳到Github

### 單元內容介紹

以後訪問網頁之後，不知道要怎麼點，請使用問問Gemini

如果不知道要如何建立repo，重複使用repo，請詢問gemini

學習思路=>應用場景->該知識點的核心名詞與知識結構，

### 實踐與檢核標準

建立 Github Repo 並上傳一份 README 說明產品客服 Agent 的初步構想與使用場景。

### 相關參考網址

https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## 單元 1：大腦核心：LLM 選擇與參數設定 (LLM & Config)

### 單元內容介紹

探討不同大型語言模型 (GPT-4, Claude, Gemini 等) 的特性。學習在 Coze 中配置模型參數 (Temperature, Max Tokens, Context Window) 對生成結果的影響。

請注意，coze對每個模型都有提供用戶基礎的免費額度，請找出目前最便宜的模型

### 實踐與檢核標準

於 Coze 平台建立一個Agent，

觀看google gemini的官網， 目前有提供哪些模型

### 相關參考網址

https://www.coze.com/open/docs/guides/llm

https://www.coze.com/open/docs/guides/model_service

https://www.coze.com/open/docs/guides/viewing_model

### 知識點

大語言的模型價格

大語言模型大小對精準度的影響

什麼是蒸餾模型

### 老師的認知

每個大模型價格不同，未來企業會在流程中引用不同模型，這時候精準度、成本與反應時間等，就成為agent設計者必須要在意的事。

大語言模型的大小意味著她能承仔的知識量，知識量對於精準度，雖沒有百分百正相關，但有正相關的影響。

蒸餾模型，就像去抄其他同學的答案

## 單元 2：Prompt的應用場景、管理流程、安全防護

### 單元內容介紹

學習撰寫高質量的 System Prompt，設定 Agent 的角色、語氣與行為規範。運用變數 (Variables) 與 Coze 的 Prompt 優化工具提升對話精準度。

必須查閱 什麼是zero shot, few shot, chain of thought,  instruction template，並知曉為什麼要透過 xml 拆解prompt

透過prompt完成 結構化輸出控制，輸出json

prompt的重複使用需求，企業對於prompt的管理剛需

必須了解 prompt injection attack，以及現在主流的防護措施以及資安單位。

### 實踐與檢核標準

撰寫客服 Agent 的 System Prompt，定義其角色、語氣與行為規範，

完成 JSON 格式輸出測試，用戶說他的年紀、職業、性別時，會轉譯成

{
  "age":20,
  "job":"學生",
  "gender": "male"
}

將prompt儲存到coze的prompt management裡面

### 相關參考網址

https://developers.openai.com/api/docs/guides/prompt-engineering

https://github.com/anthropics/prompt-eng-interactive-tutorial

https://arxiv.org/abs/2201.11903

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags

https://developers.openai.com/api/docs/guides/structured-outputs

https://genai.owasp.org/

## 單元 3：狀態管理：記憶機制 (Memory)

### 單元內容介紹

介紹 Agent 的短期與長期記憶。實作 Coze 的 Memory 功能，讓機器人能記住使用者的歷史對話、偏好設定，甚至將關鍵資訊存入變數或資料庫中。

用戶必須了解 context of round、 variable、 table 三種記憶（對話輪數、特定重點、重複行為）

知曉進階的 Memory Summarization

### 實踐與檢核標準

為agent建立一個variable，叫做 gender。

當用戶說他是什麼性別時，該variable，會進行變化紀錄。

### 相關參考網址

https://docs.langchain.com/oss/python/concepts/memory

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting

https://www.coze.com/open/docs/guides/knowledge_overview#95219b40

## 單元 4：外掛大腦：知識庫建置基礎 (Knowledge)

### 單元內容介紹

介紹檢索增強生成 (RAG) 概念。學習在 Coze 中上傳文件 (PDF, Word)、網頁連結或純文本，建立專屬 Knowledge 讓 Agent 擁有特定領域知識。

幻覺的問題，可以透過 給予額外資訊來解決， 資訊來源可以是外部 grounding，或是企業內部的pdf等檔案

資訊過於龐大，為了快速檢索，必須切割（chunking），檢索的部分允許用傳統或是ai主流的向量檢索。

要把資料轉換成給ai快速檢索讀取的向量（vector embedding），透過所謂的向量相似度（semantic similarity）做檢索

針對找到的結果做 相關性跟精準性的優先排序（top-k & reranking）

### 實踐與檢核標準

將老師提供的課程列表，作為knowledge上傳至coze。

並引入到agent，跟agent詢問課程時，有引用knowledge。

### 相關參考網址

https://www.coze.com/open/docs/guides/knowledge_overview

https://docs.langchain.com/oss/python/langchain/retrieval

ibm.com/topics/retrieval-augmented-generation

https://www.pinecone.io/learn/chunking-strategies/

https://developers.openai.com/api/docs/guides/embeddings

https://cohere.com/blog/rerank

## 單元 5：與世界接軌：內建擴充套件 (Plugin-Tool)

### 單元內容介紹

讓 Agent 擁有行動力！學習使用 Coze 豐富的內建 Plugins (如 Google 搜尋、天氣、讀取網頁、生成圖片等)，擴展機器人的能力邊界。

學生必須了解什麼是API

學生必須了解 ai--agent去訪問api 的痛點，進一步知道tools

學生必須了解 ai-agent需要一個簡略的使用手冊，進一步知道mcp與skill，就像是給ai看的產品使用手冊。

### 實踐與檢核標準

為客服 Agent 串接至少一個 Plugin -browser，當用戶發送網址問特定課程的時候，會透過browser進行爬取觀看。

### 相關參考網址

https://developers.openai.com/api/docs/guides/tools

https://modelcontextprotocol.io/specification/2025-11-25

## 單元 6：視覺化邏輯：工作流建構基礎 (Chatflow / Workflow)

### 單元內容介紹

進入進階邏輯設計。學習使用 Coze 的拖拉式 chatflow 畫布，串接 LLM 節點、透過LLM進行參數的提取、intent recognition意圖判斷、建立自動化流程。

### 實踐與檢核標準

一個chatflow的流程截圖與實際對話截圖

當用戶跟LLM說話的時候，LLM會嘗試提取出裡面是否有性別、職業、年紀、想上什麼課。

透過intent recognition 做自然語言的邏輯判斷

如果用戶是想上課的話，回應他，課程正在準備中。

如果用戶不是想上課的話，則跟他說這是課程助理。

## 單元 7：複雜場景應對：進階工作流與批次處理

### 單元內容介紹

實作更複雜的 Chatflow，透過memory、knowledge 打造一個重複對話訪談agent

### 實踐與檢核標準

一個chatflow的流程截圖與實際對話截圖

當用戶跟LLM說話的時候，LLM會嘗試提取出裡面是否有性別、職業、年紀、想上什麼課。

並將這四個參數填回variable

如果有任一個variable沒被填妥的話，會開啟一個llm 跟 用戶對話，要求填妥這個變數。

若四個參數都滿足了，會去查詢knowledge，並把knowledge結果交給llm做回應。

## 單元 8：安全與防護：安全護欄 (Guardrail)

### 單元內容介紹

探討 AI 應用的安全風險。在 Coze 中設定 Guardrail，防止 Prompt Injection (提示詞注入)、過濾不當內容，確保 Agent 的輸出符合道德與企業規範。

### 實踐與檢核標準

在chatflow的最前端與最後端，加上一個llm

並在裡面寫system prompt，這些prompt必須跟禁止特定用詞相關，比如提及 情色內容

## 單元 9：多方協作與發布部署 (Multi-Agent & Publish)

### 單元內容介紹

完成的 Agent 一鍵發布至 Line, Discord, Telegram 或網頁端。

並透過coze進行長期監控，了解token的使用狀況

### 實踐與檢核標準

將產品客服 Agent 部署至Line，

並截圖該agent的 coze後台監控畫面。

## 單元 10：期末專題發表與評估

### 單元內容介紹

學生展示最終的AI Agent 專題。評分標準包含：功能完整性 (Workflow/Plugin 應用)、知識檢索準確度、防護機制，以及實際部署的可用性。

### 實踐與檢核標準

展示最終完整的產品客服 Agent，並驗證其功能、知識檢索準確度與部署可用性。

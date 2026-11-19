# IBKR 外匯與保證金：讀書筆記（2026-11-19）

目的：老師 2026-11-18 建議研究外匯；使用者 2026-11-19 決定**外匯可以納入專題**（範圍還沒定）。這份只整理 IBKR 官方頁面寫了什麼，**不含任何帳戶數字**，也不是投資建議。每條標明來源是「讀過原文」或「只有搜尋摘要」。

## 讀過原文的（用內建瀏覽器開官方頁，2026-11-19）

1. **IdealPro 是什麼、最低量**（[FAQ：What does the IdealPro minimum mean?](https://www.interactivebrokers.com/support/faq/content/idealpro-minimum-mean-65996956)）
   - IdealPro 是 IBKR 執行外匯的場地，像交易所的委託簿，匯集大型外匯銀行與交易商、其他 IBKR 客戶、做市商的報價。
   - 所有 IdealPro 訂單**最低 25,000 美元或等值**；低於這個量是 odd lot，限價不會透過 IdealPro 公開。
   - odd lot 的可成交限價單仍會被接受，但**不保證**以銀行間價差成交，一般會比 IdealPro 報價**差 1～2 個基點**，也可能較慢成交。
2. **外匯餘額也有保證金**（[FAQ：Is there a margin calculation for FX balances…](https://www.interactivebrokers.com/support/faq/content/there-margin-calculation-fx-balances-41560254)）
   - 帳戶持有非基準貨幣時，可能有保證金要求。方法：把各非基準貨幣的淨清算值換算成基準貨幣，對每個貨幣對取「折減率（haircut）」，找出最大的負餘額，再用折減率最低的正餘額去抵銷，逐步算到所有負餘額被覆蓋。
3. **幣別保證金計算範例**（[FAQ：Currency margin calculation](https://www.interactivebrokers.com/support/faq/content/currency-margin-calculation-1163245559)）
   - 範例（基準貨幣 USD）：EUR 為負、KRW 與 USD 為正；折減率 USD/EUR 為 0.025、USD/KRW 與 EUR/KRW 為 0.10；先用折減率最低的正餘額抵銷負餘額，各段乘以折減率後相加得總保證金。**範例的數字是 IBKR 示範用，不是我的帳戶。**
   - 這個算法和我專題目前的壓力測試（假設全部多頭美股、維持保證金與市值成正比）**不是同一種**：外匯餘額的保證金看「各幣別淨額之間的抵銷」，不是持倉市值乘固定比例。
4. **外匯保證金比例表（只讀到 IB Canada 版）**（[Full List of IB Canada Regulator Margin Rates for Forex](https://www.interactivebrokers.com/en/trading/marginRequirements/margin_canadian_currencies.php)）
   - 這頁標的是 **IB Canada 監管機構**的維持保證金：例如 EUR.USD、GBP.USD、JPY.USD 3.0%（約 33.3:1），CAD.USD 2.0%（50:1），HKD、SGD 10%（10:1），DKK、ILS、PLN 25%（4:1）。
   - 頁尾：保證金比例 = 1 ÷ 槓桿倍數；美國 IRA 保證金帳戶**不得借入非基準貨幣**。
   - **這是加拿大版，不能直接當作我的帳戶適用的數字。**
5. **保證金頁本身沒有外匯入口**：`margin-requirements.php` 列出股票、期權、期貨、單一股票期貨、固定收益、共同基金、美國金屬的連結，**我在頁面文字裡找不到「forex」**。原本猜的 `margin-forex.php` 網址回 410（已不存在）。

## 只有搜尋摘要、沒有讀到原文的（不要當查證結果用）

- 外匯貨幣對的舊版標準比例（搜尋摘要提到某份舊文件列 EUR、GBP 約 2%、JPY 約 3%、CHF 約 5%；另一個摘要說「所有貨幣對初始 5%、維持 3%」）——**兩者互相不一致，來源又是舊文件，不採用**。
- 外匯佣金（摘要說 IDEALPRO 佣金為交易貨幣價值的 0.00002 倍、每筆最低 2.5 美元等值）——來自佣金 PDF 的摘要，沒開原文。
- 外匯下單操作步驟（輸入 `EUR.USD`、Buy 是買第一個貨幣、可在數量欄切換幣別、T+1 結算）——來自搜尋摘要引用 IBKR 支援與 Campus 內容，**沒有讀到原文**。

## 對專題的意義（推論，未驗證）

- 老師說外匯「入門比較不會賠錢」。**我沒有查證這句話**；至少官方資料顯示：外匯有保證金（Canada 版約 2～25%，視貨幣對）、odd lot 成交價可能差 1～2 個基點、外幣餘額為負時也要算保證金。這些都和「流動性 → 維持保證金 → 購買力」同一條因果鏈有關，所以外匯**適合納入驗算範圍**，但它的保證金算法和目前的程式不同。
- 若要把外匯納入專題，目前缺的是：①適用我的帳戶（美國 IBKR LLC 或其他）的外匯保證金比例（本次沒讀到）②模擬帳戶是否能交易外匯 ③外匯餘額保證金的驗算程式（`experiments/` 只有股票型）。這三項都還沒做。
- 專題界線不變：外匯下單由使用者本人在模擬帳戶手動做，Agent 與程式不下單，也不建議買賣哪個貨幣對。

## 範圍決定（2026-11-19，使用者）

外匯納入專題的方式：**讀懂**（官方規則）、**驗算**（外匯保證金的欄位稽查）、**當資料面**（匯率、外幣餘額進分析）三者都要。還沒定的：驗算程式怎麼寫（外匯是各幣別淨額抵銷，與現有程式不同）、適用我帳戶的比例來源、模擬帳戶能否交易外匯。這些要先確認再動手，不要用 Canada 版比例或搜尋摘要的舊數字去寫程式。

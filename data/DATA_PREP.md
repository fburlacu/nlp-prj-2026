# Data Preprocessing

## 1. Data sources

**EEAS EUvsDisinfo database.** A CSV export of the EUvsDisinfo database maintained by the European External Action Service. Each case contains `Date`, `Links` (the `/report/<slug>` URL), `Title`, `Outlets`, `Country`, `Disinformation` (an analyst-written summary of the claim) and `Information` (the analyst-written disproof). The database contains only disinformation cases.

**Leite et al. (2024) EUvsDisinfo dataset.** An article-level dataset derived from the EEAS debunks (CIKM 2024; Zenodo record 10514307). Each row is an article cited in a debunk, with `debunk_id`, `keywords`, `article_id`, `article_publisher`, `article_domain`, `article_url`, `article_language`, `debunk_date` and `class`. The class is either `disinformation` (the article spread the debunked claim) or `trustworthy` (the article was cited as evidence in the disproof). For copyright reasons the authors distribute URLs only, not article texts.

## 2. Restriction to English

We keep the English rows of the Leite dataset (`article_language` = English: 425 disinformation, 6,121 trustworthy articles) and the full EEAS database, whose summaries and disproofs are written in English.

We restrict to English for four reasons:

1. **Isolating the variable under study.** The research questions compare sparse, dense and hybrid retrieval. Fixing the language removes cross-lingual effects as a confounder, so any differences can be attributed to the retrieval method.
2. **Avoiding a label shortcut.** Across all languages, trustworthy articles are predominantly English, while disinformation articles are mostly in other languages (notably Russian). In a multilingual set, language alone would predict the class.
3. **Resource constraints.** Lightweight English tokenisers and embedding models are stronger and cheaper than multilingual alternatives. This matters for a small university server and a five-week timeline.
4. **Consistency with the knowledge base.** The EEAS summaries and disproofs, which form the core of the evidence store, are already in English.

**Limitations.** Results may not transfer to non-English disinformation, which makes up most pro-Kremlin output. English disinformation articles are scarce (425) and may be atypical, for example outlets that target Western audiences. The EEAS texts are English renderings of claims that originally appeared in many languages, so the system judges analysts' summaries rather than the original wording. Extending the comparison to multilingual retrieval is left for future work.

### 2.1 Language distribution of the Leite dataset
 
The table shows the class distribution of the 20 most frequent languages in the full Leite dataset (18,249 articles). `trust_share` is the fraction of a language's articles labelled trustworthy.
 
| Language | Disinformation | Trustworthy | Total | Trust share |
|---|---:|---:|---:|---:|
| **All languages** | **10,682** | **7,567** | **18,249** | **0.41** |
| English | 425 | 6,121 | 6,546 | 0.94 |
| Russian | 5,356 | 469 | 5,825 | 0.08 |
| Arabic | 3,449 | 2 | 3,451 | 0.00 |
| Ukrainian | 8 | 315 | 323 | 0.98 |
| German | 216 | 97 | 313 | 0.31 |
| French | 165 | 127 | 292 | 0.43 |
| Spanish | 243 | 44 | 287 | 0.15 |
| Georgian | 146 | 10 | 156 | 0.06 |
| Czech | 111 | 41 | 152 | 0.27 |
| Polish | 44 | 103 | 147 | 0.70 |
| Hungarian | 144 | 3 | 147 | 0.02 |
| Italian | 85 | 18 | 103 | 0.17 |
| Armenian | 83 | 4 | 87 | 0.05 |
| Lithuanian | 28 | 50 | 78 | 0.64 |
| Romanian | 17 | 51 | 68 | 0.75 |
| Azerbaijani | 54 | 0 | 54 | 0.00 |
| Slovak | 32 | 3 | 35 | 0.09 |
| Serbian | 27 | 4 | 31 | 0.13 |
| Finnish | 8 | 22 | 30 | 0.73 |
 
The class balance varies sharply by language. English (0.94) and Ukrainian (0.98) are almost entirely trustworthy, while Russian (0.08), Arabic (0.00), Hungarian (0.02) and Azerbaijani (0.00) are almost entirely disinformation. Across the full dataset, language is therefore a strong proxy for the label. English is the largest language subset, but within it disinformation articles are a small minority (425 of 6,546, about 6.5%).

## 2.3 Limitations

 
**Narrative coverage is multilingual.** The English restriction is partly offset by keeping the full EEAS database. EEAS documents disinformation from every source language and describes each case in English. The knowledge base and the main disinformation queries therefore cover the full range of pro-Kremlin narratives, including those that only appeared in Russian, Arabic, Hungarian or other languages.
 
**Original formulation is mostly not covered.** The EEAS summaries are analyst paraphrases written in a neutral reporting style. They largely remove the features that characterise propaganda: loaded language, framing and emotional appeals. Non-English disinformation is thus represented only through English paraphrases. Formulation-driven effects (RQ1) are evaluated mainly on the smaller set of English-language disinformation articles (425), which keep their original wording. These articles may also be atypical, for example outlets that target Western audiences.

**Possible extension.** To recover some original formulation, a sample of the Russian-language disinformation articles (about 5,000 available) could be machine-translated into English with a lightweight model (e.g. Opus-MT ru-en) and added as extra hard queries. This keeps the original framing, filtered through translation, and will be done only if time allows.

## 3. Article text collection

The Leite dataset ships URLs only. The authors' collection software relies on the Diffbot API, which was not available to us. We therefore wrote our own crawler:

- **Extraction.** Each page is fetched with `requests` and its main text and title are extracted with the open-source library `trafilatura` (precision-oriented settings).
- **Fallback.** Articles that fail on the live web (HTTP errors, empty extraction) are retried in a second pass via the Wayback Machine's closest archived snapshot.
- **Scope.** Only English rows are crawled. A cleaning step removes any non-English or malformed entries from the crawl cache, keeping a backup of the original.
- **Logging.** All failures are recorded with their reason (`errors.jsonl`). The crawl is resumable.
- **Usage.** Article texts are used for this research only and are not redistributed.

**Crawl yield.** The crawl was run as a fast first pass over all English articles. Failed articles can be retried via the Wayback Machine (see above).
 
| Class | English articles | Crawled | Yield |
|---|---:|---:|---:|
| Trustworthy | 6,121 | 4,016 | 66% |
| Disinformation | 425 | 318 | 75% |
| **Total** | **6,546** | **4,334** | **66%** |
 
Failures were mostly unreachable or blocked pages, timeouts and pages without extractable article text. The yield is lower than that of the Diffbot-based collection used by the dataset authors.

## 4. Label semantics and cleaning of the Leite dataset
 
**How labels are assigned.** Each row of the Leite dataset is a (debunk, article) pair: an article cited in one EEAS debunk, together with its role in that debunk. According to Leite et al. (2024, Sec. 2), the `class` field is determined by where the link appears on the debunk web page:
- `disinformation`: links listed on the left-hand side of the page, where EEAS records the sources that spread the claim. This corresponds to the `Outlets` column of the EEAS database, not to the text of the `Disinformation` summary.
- `trustworthy`: links to sources cited in the response section, where EEAS debunks the narrative. This corresponds to the `Information` (disproof) text.
The label therefore describes the article's role in a debunk rather than a reliability judgment made about the article itself. The rows contain no debunk content beyond `keywords` and `debunk_date`. The claim and disproof are only available by linking `debunk_id` to an EEAS case (Section 5).
 
**Quality controls by the dataset authors.** Leite et al. checked whether response sections link to disinformation. They manually annotated all 350 URLs in the response sections of 30 randomly sampled debunks, and found that every link in a disinformation context (e.g. after "see similar cases") pointed to other debunks or fact-checkers such as Bellingcat and StopFake, not to disinformation articles. They also removed:
- 12,875 URLs whose domain is not a news outlet;
- 4,048 error pages, log-in prompts, paywalls and texts shorter than 700 characters;
- 667 URLs cited in sentences referring to other fact-checking articles (e.g. "See earlier disinformation cases").
**Repeated articles.** The same article can appear in several rows. A disinformation article may contain several claims that are debunked as separate cases, a credible source may be cited as evidence in many debunks, and recurring narratives are re-debunked with links to older articles. Article texts are therefore crawled once per `article_id` and merged back onto all of the article's rows. In the index and the query set, each article is used only once. For leakage exclusion and splitting, all of its debunk links are kept, so an article never appears in more than one split.
 
**Articles with both labels.** Some articles are labelled `disinformation` in one debunk and `trustworthy` in another. Given the authors' checks, systematic links from disproofs to disinformation and non-article links are unlikely causes. More plausible explanations are that an outlet's article is cited as a factual source in one debunk (for example, for an official statement it reports) while being listed as a source of the claim in another, or that it mixes a debunked claim with a correct statement. The authors' manual check covered only 30 debunks, so residual labelling noise cannot be excluded.
 
*Cleaning rules:**
1. Texts shorter than 700 characters are removed, consistent with the dataset authors' filter for error pages, paywalls and stubs.
2. Texts whose opening matches a boilerplate lexicon (JavaScript or captcha prompts, access-denied and not-found pages, subscription walls, cookie walls) are removed.
3. Documents (by `doc_key`) with both labels are removed as ambiguous, regardless of the cause.
4. Documents whose text is not detected as English (`langdetect`, first 1,000 characters) are removed. This matters because Leite et al. inferred the language of trustworthy articles automatically.
5. `trustworthy` rows from domains whose rows are predominantly (> 80%) `disinformation` are inspected as a diagnostic. They are removed only if manual inspection confirms that they are pro-Kremlin articles rather than credible evidence.
**Cleaning results.**
 
| Step | Rows | Documents | Removed |
|---|---:|---:|---|
| English rows in the Leite base file | 6,546 | 6,546 | |
| Crawled successfully | 4,334 | 4,334 | 2,212 (unreachable, blocked or failed extraction) |
| Text ≥ 700 characters | 4,084 | 4,084 | 250 (stubs, error pages) |
| No boilerplate | 4,084 | 4,084 | 0 |
| No documents with both labels | 4,084 | 4,052 | 0 rows; 32 rows repeat a document under another debunk |
| Text detected as English | 4,055 | 4,036 | 16 documents not in English |
| **Final** | **4,055** | **4,036** | |
 
The final data contains **3,733 trustworthy** and **303 disinformation** documents. Three trustworthy documents were flagged by rule 5 and are pending manual inspection.

## 5. Linking articles to EEAS cases

The Leite `debunk_id` is a UUID with no direct correspondence to the EEAS report slug, so articles are linked to cases heuristically:

1. **Candidate cases.** For each disinformation article, a case is a candidate if its EEAS `Date` is within ±3 days of `debunk_date` and the `article_publisher` or `article_domain` appears in the case's `Outlets`.
2. **Majority vote.** Candidates are aggregated per `debunk_id` by majority vote over its disinformation articles. Ties are discarded rather than guessed.
3. **Conflicts.** Debunks mapped to a case that is also claimed by another `debunk_id` are discarded.



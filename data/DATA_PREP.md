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

The Leite `debunk_id` is a UUID with no direct correspondence to the EEAS report slug.


## 6. EEAS query analysis and construction

### 6.1 Initial analysis
 
**Lexical overlap.** Overlap is the share of a title's words that also appear in a disproof. A first analysis on exact word forms (lowercased tokens of three or more letters) gave a mean overlap of 0.49 with the own disproof versus 0.18 with a random other disproof. The baseline reflects shared domain vocabulary (e.g. Russia, Ukraine, NATO). The additional overlap is case-specific: names, places and terms of the claim reappear in its disproof, partly because a disproof restates the claim in order to refute it. Real-world claims are unlikely to match their evidence this closely, which may favour lexical retrieval (BM25) on EEAS-title queries.
 
**Issues found:**
- **Length confounder.** In overlap tertiles, the low-overlap bin had much shorter disproofs (median 50 words vs. 172 and 209), so low overlap partly reflected little evidence text rather than different wording.
- **Zero-overlap titles** were partly genuine paraphrases (e.g. "labs … bioweapons" vs. "laboratories … biological weapons") and partly morphological variants ("Crimeans" vs. "Crimea") missed by exact matching.
- **Reused and placeholder disproofs.** Many disproofs reuse standard text for recurring narratives, and some are placeholders without evidence (e.g. "No evidence given.").

### 6.2 Query pool
 
All query statistics use the same preprocessing as the BM25 retriever ( lowercasing, English stopword removal, Snowball stemming). 

The query pool contains cases with a title and a disproof of at least 30 words: **12,354 of 14,497 cases** (2,143 excluded). With BM25 tokens, mean title overlap is **0.56 with the own disproof versus 0.12 with a random disproof**. Stemming matches morphological variants, and stopword removal removes generic words from the baseline.
 
| Overlap bin | Overlap range | Cases | Median disproof length (words) |
|---|---|---:|---:|
| Low | 0.00–0.44 | 4,234 | 124 |
| Mid | 0.45–0.67 | 4,253 | 186 |
| High | 0.69–1.00 | 3,867 | 213 |
 
After excluding very short disproofs, the length confounder is weaker but still present. It is controlled through sampling.

### 6.3 Near-duplicate cases
 
Two cases are **near-duplicates** if their disproofs share at least 80% of their word 5-grams (Jaccard ≥ 0.8) or their titles share at least 80% of their words. This detects copied text, not semantically similar debunks: two independently written refutations of the same narrative are not near-duplicates. Candidate pairs are found with MinHash LSH and verified with exact Jaccard. Disproofs shorter than 10 words (705 cases, mostly placeholders such as "No evidence given.") are excluded from disproof matching, since identical placeholders would otherwise form one large spurious cluster.
 
| Statistic | Value |
|---|---:|
| Near-duplicate disproof pairs | 1,701 |
| Near-duplicate title pairs | 430 |
| Cases with at least one near-duplicate | 1,863 (in 735 groups) |
| Direct near-duplicates per pool case | mean 0.26, max 21 |
 
Most near-duplicates are different claims sharing a standard refutation (different titles, same disproof text), or the same claim debunked again (same title, different disproof). Both are a real property of the database, and all near-duplicates remain in the index.
 
Near-duplicates are used in two ways:
- **Lenient gold.** For each case, the lenient gold set is the case itself plus its *direct* near-duplicates. Transitive groups are not used for scoring, because chaining (A ≈ B, B ≈ C) can join cases whose texts are not similar.
- **Held-out cases.** Only cases without any near-duplicate (group size 1) are held out for inconclusive queries, so that no copy of their evidence remains in the index.

### 6.4 Sampled EEAS queries
 
| Query set | Size | Sampling | Gold |
|---|---:|---|---|
| Disinformation (EEAS titles) | 345 (300 test, 45 dev) | 115 per overlap bin, equally spread over disproof-length tertiles; cases with more than 10 direct near-duplicates (35) excluded | Strict: own disproof. Lenient: own disproof or a direct near-duplicate |
| Inconclusive (held-out EEAS titles) | 345 (300 test, 45 dev) | Stratified by year; only cases without near-duplicates | None. The case is removed from the index (`held_out_links.csv`) |
 
Median disproof length in the sampled disinformation queries is 173, 194 and 181 words for the low, mid and high overlap bins, so the bins differ in wording overlap rather than in amount of evidence text.
 
**Limitation of the inconclusive set.** Excluding near-duplicates removes copied evidence, but not independently written debunks of the same recurring narrative. For some held-out claims, the system may therefore find valid evidence and correctly answer "disinformation". These cases are scored separately rather than counted as errors.
 
**Retrieval scoring (planned).** Retrieval is reported per overlap bin, under the strict and the lenient criterion. For disinformation queries, the case's own claim passage is excluded at retrieval time.

## 7. Leite query construction
 
Leite article titles provide the fact queries (trustworthy articles) and a second set of disinformation queries in their original wording (disinformation articles). Queries are built per document (`doc_key`), not per row.
 
### 7.1 Title cleaning
 
Site names are stripped from titles ("NATO rejects Russian claims - BBC News" → "NATO rejects Russian claims"): a title is split on separators (`|`, `-`, `–`, `—`, `:`), and side parts of at most four words are removed. Documents without a usable title are dropped. This leaves 3,728 trustworthy and 303 disinformation documents.
 
### 7.2 Fact queries
 
**Fact-check exclusion.** Fact-checking articles cited in disproofs are often titled with the false claim they debunk (e.g. "Fact check: The Ukrainian military burned the Koran"). Title cleaning would strip the short prefix and leave a false claim labelled as fact. Trustworthy titles matching a fact-check / claim-reporting lexicon (fact check, fake, false, myth, debunk, hoax, misleading, disinformation, propaganda, claim(s), conspiracy, fabricated, not true) are therefore excluded from the fact queries. The lexicon is applied to the raw title, before cleaning, so that such prefixes are still visible. It is deliberately broad and also removes some ordinary reported claims ("Kremlin claims …"); this is acceptable given the surplus of candidates. **250 titles** were excluded (`excluded_factcheck_titles.csv`). These documents remain in the index as evidence.
 
**Claim filter.** A trustworthy title is a fact query only if it asserts a checkable claim. Two filters are combined:
- **Rule-based:** at least five words, not a question, and not starting with a format label ("Live", "Watch", "Opinion", "Explainer", "How", "What", …).
- **LLM-based:** Qwen2.5-7B-Instruct with a few-shot yes/no prompt. The verdict is scored from the next-token probabilities of "Yes" and "No" (no sampling, deterministic).
Inspection of the full run showed that between p(yes) ≈ 0.05 and 0.5, claims and non-claims overlap considerably. Because candidates are plentiful, the threshold was set for precision: **p(yes) ≥ 0.5 and the rule filter**, which keeps **1,994 of 3,728** titles (53%).
 
**Debunk cap.** At most one document per debunk is used, counting all debunks a document is cited in, so no narrative dominates the fact queries.
 
### 7.3 Leakage control and splits
 
Documents are grouped into **leakage groups**: connected components over shared debunks (using all of a document's debunk links) and near-identical titles (word Jaccard ≥ 0.9, typically wire copies on several sites). Each group is assigned as a whole to dev (about 15% of groups) or test. Groups used in the article set, in either class, are excluded from the main set. As a result, no debunk or wire copy crosses dev/test or the two sets; the build script asserts this.
 
For self-retrieval exclusion, every Leite query lists its own `doc_key` and the documents with near-identical titles in `exclude_doc_key`. These are removed from the retrieval results for that query.
 
### 7.4 Sampled Leite queries
 
| Query set | Label | Source | Sampling |
|---|---|---|---|
| Main | fact | Claim-like trustworthy titles | 345 (300 test, 45 dev), year-matched to the EEAS disinformation queries |
| Article | disinformation | All 303 English disinformation titles | No claim filter (too few to spare); 23 would fail the rule filter. Split by leakage group |
| Article | fact | Claim-like trustworthy titles | Same number as the disinformation articles per split, year-matched to them |
 
Year matching (largest-remainder allocation over years) prevents the classes from being separable by period. Documents without a parseable year can only enter through top-up sampling.
 
### 7.5 Proxy gold for article-level disinformation queries
 
Leite queries have no exact gold evidence, because they cannot be linked to EEAS cases (Section 5). For disinformation article queries, we use **proxy relevance labels**: the trustworthy documents cited in the same EEAS debunk(s), i.e. the sources analysts chose to refute that claim, excluding the query's own document and wire copies (`gold_doc_keys`).
 
- **Coverage:** 67 of 303 disinformation article queries have at least one such document.
- **Scoring:** a hit if any chunk of a gold document is retrieved (proxy recall@k, MRR), reported on the test queries with proxy gold, with paired bootstrap confidence intervals.
- **Fairness:** the labels come from analysts' citations, not from text similarity, so they favour no retrieval method.
- **Limitations:** the labels are incomplete (other valid evidence, such as the unlinked EEAS disproof, counts as a miss), so absolute recall is underestimated. Some cited sources are background rather than refutation. Given the small sample, these results are exploratory and are used only to check whether the retriever ranking observed on EEAS titles also holds for original headlines.
Fact queries have no gold evidence, since other articles from the same debunk may be background rather than corroboration. They are scored on the verdict only.
 
### 7.6 Style-shortcut check
 
A TF-IDF + logistic regression classifier trained on query text alone (no retrieval) indicates how far labels can be predicted from wording (5-fold macro-F1):
 
| Set | Classes | Macro-F1 | Chance |
|---|---|---:|---:|
| Main | disinformation / fact | 0.83 | 0.50 |
| Main | disinformation / fact / inconclusive | 0.52 | 0.33 |
| Article | disinformation / fact | 0.63 | 0.50 |
 
In the main set, disinformation queries are analyst-written EEAS titles while fact queries are journalist headlines, so the two classes are largely separable by style. Disinformation and inconclusive queries are both EEAS titles and cannot be separated from text alone, so only retrieval can distinguish them. In the article set, both classes are news headlines and the shortcut is much weaker. The text-only classifier is therefore reported as a no-retrieval baseline. RAG results on the main set are interpreted against it, and the article set serves as the main test of whether retrieved evidence improves detection.
 
## 8. Final query set (`queries.csv`)
 
`queries.csv` combines the EEAS and Leite queries. Only the `text` column is passed to the retriever and the LLM; all other columns are metadata for filtering, scoring and analysis.
 
| Set | Label | Source | Dev | Test |
|---|---|---|---:|---:|
| Main | disinformation | EEAS titles (case in the index) | 45 | 300 |
| Main | inconclusive | EEAS titles (case held out of the index) | 45 | 300 |
| Main | fact | Leite trustworthy titles | 45 | 300 |
| Article | disinformation | Leite disinformation titles | by group (~15%) | remainder of 303 |
| Article | fact | Leite trustworthy titles | same as disinformation | same as disinformation |
 
**Why two sets.** The main set provides exact retrieval gold (RQ1) and the inconclusive class, but mixes analyst-written disinformation queries with journalist-written fact queries. The article set uses original headlines for both classes and is therefore the realistic, style-matched test of detection (RQ2), but has only proxy retrieval gold for a subset. The main set is the primary benchmark; the article set checks whether the findings hold on real headlines.
 
**Columns.**
 
| Column | Content | Used for |
|---|---|---|
| `query_id` | Unique ID (`eeas_dis_…`, `eeas_inc_…`, `leite_fact_main_…`, `leite_fact_art_…`, `leite_dis_art_…`) | Joining results |
| `text` | EEAS title or cleaned Leite headline | The only pipeline input |
| `label` | disinformation / fact / inconclusive | Detection scoring (RQ2) |
| `set`, `split` | main / article; dev / test | Test set, tuning vs reporting |
| `source` | `eeas_title` / `leite_title` | Provenance |
| `gold_links` | Own case `Links` (EEAS disinformation only) | Strict retrieval scoring (RQ1) |
| `gold_links_lenient` | Own case plus direct near-duplicates | Lenient retrieval scoring |
| `gold_doc_keys` | Same-debunk trustworthy documents (article-set disinformation only) | Proxy retrieval scoring |
| `exclude_passage_ids` | Own claim passage (EEAS disinformation) | Self-retrieval exclusion |
| `exclude_doc_key` | Own document and wire copies (Leite queries) | Self-retrieval exclusion |
| `case_links` | Case the EEAS title came from | Tracing; held-out case for inconclusive queries |
| `overlap`, `overlap_bin`, `disproof_len` | Title–disproof overlap, its bin, disproof length (EEAS) | RQ1 results per bin; length control |
| `date` | Case date / `debunk_date` | Year matching, time coverage |
| `doc_key`, `debunk_id`, `leak_group` | Document, all its debunks, leakage group (Leite) | Tracing, leakage control |
 
**Known caveats.**
1. **Style shortcut in the main set** (Section 7.6). Reported as a text-only baseline.
2. **Lexical closeness of EEAS titles to their evidence** (Section 6.2), addressed by reporting results per overlap bin.
3. **"Fact" is a proxy:** a cited trustworthy source with a claim-like title, not a verified true claim.
4. **No exact retrieval gold for Leite queries** (Section 5): article-level retrieval is evaluated only through proxy gold for 67 queries.
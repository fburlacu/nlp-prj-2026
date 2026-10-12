"""Crawl English Leite EUvsDisinfo articles (both classes) without Diffbot.

pip install trafilatura pandas requests tqdm
Usage:
  python crawl_english.py --test                 # try 5 URLs
  python crawl_english.py                        # fast first pass (no Wayback)
  python crawl_english.py --retry-failed --wayback   # second pass on failures
Resumable: already-crawled articles in cache.jsonl are skipped.
"""
import os, json, time, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests, trafilatura, pandas as pd
from tqdm import tqdm

CACHE, ERRLOG = "cache.jsonl", "errors.jsonl"
UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")}
TIMEOUT = 20
lock = threading.Lock()


def append(path, obj):
    with lock, open(path, "a") as f:
        f.write(json.dumps(obj, default=str) + "\n")


def extract(url):
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    if r.status_code != 200:
        return None, f"http {r.status_code}"
    text = trafilatura.extract(r.text, favor_precision=True)
    meta = trafilatura.extract_metadata(r.text)
    return ({"text": text, "title": meta.title if meta else None}, None) if text else (None, "no text")


def is_english(lang):
    return str(lang).strip().lower() in {"english", "en"}


def clean_cache(path=CACHE):
    """Remove non-English rows from the cache file (keeps a .bak backup)."""
    if not os.path.exists(path):
        return
    kept, removed = [], 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                removed += 1
                continue
            if is_english(row.get("article_language")):
                kept.append(line if line.endswith("\n") else line + "\n")
            else:
                removed += 1
    os.replace(path, path + ".bak")
    with open(path, "w") as f:
        f.writelines(kept)
    print(f"Cache cleaned: kept {len(kept)}, removed {removed} (backup: {path}.bak)")


wb_slots = threading.Semaphore(2)  # archive.org rate-limits; keep concurrency low


def wayback(url):
    """Return closest Wayback snapshot URL, or None (never raises on bad responses)."""
    with wb_slots:
        for attempt in range(3):
            try:
                r = requests.get("https://archive.org/wayback/available",
                                 params={"url": url}, timeout=30)
                if r.status_code == 200:
                    snap = r.json().get("archived_snapshots", {}).get("closest", {})
                    return snap.get("url") if snap.get("available") else None
            except (ValueError, requests.RequestException):
                pass  # non-JSON (rate-limit page) or network error
            time.sleep(5 * (attempt + 1))  # back off before retrying
        return None


def process(row, use_wayback):
    url = row["article_url"]
    try:
        res, err = extract(url)
        if not res and use_wayback:
            wb = wayback(url)
            if wb:
                res, wb_err = extract(wb)
                err = None if res else f"{err} | wayback: {wb_err}"
            else:
                err = f"{err} | no wayback snapshot"
    except Exception as e:
        res, err = None, repr(e)
    if res:
        append(CACHE, {**row, "article_text": res["text"], "article_title": res["title"]})
        return True
    append(ERRLOG, {"article_id": row["article_id"], "url": url, "error": err})
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="euvsdisinfo_base.csv")
    ap.add_argument("--classes", nargs="*", default=["trustworthy", "disinformation"])
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--wayback", action="store_true", help="fall back to archive.org")
    ap.add_argument("--retry-failed", action="store_true", help="only crawl ids in errors.jsonl")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--skip-failed", action="store_true",
                    help="do not re-attempt articles already logged as failed")
    ap.add_argument("--clean-only", action="store_true", help="only clean cache.jsonl, then exit")
    a = ap.parse_args()

    clean_cache()
    if a.clean_only:
        raise SystemExit

    df = pd.read_csv(a.base)
    df = df[df["article_language"].apply(is_english)]
    df = df[df["class"].isin(a.classes)]
    print("English articles in scope:", len(df), dict(df["class"].value_counts()))

    if os.path.exists(CACHE):
        done = set(pd.read_json(CACHE, lines=True)["article_id"])
        df = df[~df["article_id"].isin(done)]
    if a.skip_failed:
        logs = [p for p in (ERRLOG, ERRLOG + ".prev") if os.path.exists(p)]
        failed = set().union(*(set(pd.read_json(p, lines=True)["article_id"]) for p in logs)) if logs else set()
        df = df[~df["article_id"].isin(failed)]
        print("Skipping previously failed:", len(failed))
    if a.retry_failed and os.path.exists(ERRLOG):
        failed = set(pd.read_json(ERRLOG, lines=True)["article_id"])
        df = df[df["article_id"].isin(failed)]
        os.rename(ERRLOG, ERRLOG + ".prev")  # fresh error log for this pass
    rows = df.astype(object).where(df.notna(), None).to_dict("records")
    print("To crawl now:", len(rows))

    if a.test:
        for r in rows[:5]:
            print(r["article_url"], "->", extract(r["article_url"])[1] or "OK")
        raise SystemExit

    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(process, r, a.wayback) for r in rows]
        ok = sum(f.result() for f in tqdm(as_completed(futs), total=len(futs)))
    print(f"OK: {ok} | failed: {len(rows) - ok} (see {ERRLOG})")

    out = pd.read_json(CACHE, lines=True).drop_duplicates("article_id")
    out = out[out["article_language"].apply(is_english)]
    out.to_csv("euvsdisinfo_en.csv", index=False)
    print("Wrote euvsdisinfo_en.csv:", len(out), "rows", dict(out["class"].value_counts()))
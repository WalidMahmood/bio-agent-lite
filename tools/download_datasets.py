"""Download GEO datasets via FTP (NCBI browser is bot-blocked, FTP works).
Usage: python tools/download_datasets.py [--only GSE202768]
"""
import argparse, os, sys, urllib.request, gzip, shutil, tarfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANIFEST = {
    "GSE202768": {
        "base": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE202nnn/GSE202768",
        "files": ["matrix/GSE202768_series_matrix.txt.gz",
                  "suppl/GSE202768_TNBC_Cell_line_PRRX1_KD_RNAseq_Gene_Counts.csv.gz",
                  "suppl/GSE202768_TNBC_Cell_line_PRRX1_KD_RNAseq_Gene_FPKM.csv.gz"],
    },
    "GSE336903": {
        "base": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE336nnn/GSE336903",
        "files": ["matrix/GSE336903_series_matrix.txt.gz",
                  "suppl/GSE336903_Fig7_cell_line_FPKM_matrix_GEO.csv.gz"],
    },
    "GSE95304": {
        "base": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE95nnn/GSE95304",
        "files": ["matrix/GSE95304_series_matrix.txt.gz",
                  "suppl/filelist.txt",
                  "suppl/GSE95304_RAW.tar"],
    },
    "GSE113650": {
        "base": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE113nnn/GSE113650",
        "files": ["matrix/GSE113650_series_matrix.txt.gz",
                  "suppl/GSE113650_RNA-seq_BRCA_CellLine_CuffDiff_GEO_submit.txt.gz"],
    },
}

def dl(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  SKIP exists {dest} ({os.path.getsize(dest)} bytes)")
        return dest
    print(f"  GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "BioAgent-Lite/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    print(f"  SAVED {dest} ({os.path.getsize(dest)} bytes)")
    return dest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--skip-raw-tar", action="store_true", default=False,
                    help="skip GSE95304_RAW.tar (can be large)")
    args = ap.parse_args()
    for acc, m in MANIFEST.items():
        if args.only and acc != args.only:
            continue
        print(f"== {acc} ==")
        for rel in m["files"]:
            if args.skip_raw_tar and rel.endswith("_RAW.tar"):
                print(f"  SKIP --skip-raw-tar {rel}")
                continue
            url = m["base"] + "/" + rel
            dest = os.path.join(BASE, "data", "raw", acc, os.path.basename(rel))
            try:
                dl(url, dest)
            except Exception as e:
                print(f"  FAIL {rel}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

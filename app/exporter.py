import os
import shutil as sh
import zipfile
from pathlib import Path
from typing import Dict, Optional

from google.cloud import storage

_DOC_EXT = {".pdf", ".tif", ".tiff", ".png", ".jpg", ".jpeg"}


def is_document(fname: str) -> bool:
    return Path(fname).suffix.lower() in _DOC_EXT


# ------------------------------------------------------------------
# 1️⃣  CREA .dat + ZIP  (rimane invariata, ma restituisce il path)
# ------------------------------------------------------------------
def zip_and_export(
    metadata: str,
    *,
    tmp_dir: str = "tmp",
    zip_path: str = "solution.zip",
    dat_name: str = "DocumentsOfRecord.dat",
) -> str:
    with open(dat_name, "w", newline="") as f:
        f.write(metadata)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(dat_name, arcname=dat_name)
        for f_name in os.listdir(tmp_dir):
            p = os.path.join(tmp_dir, f_name)
            if os.path.isfile(p) and is_document(f_name):
                zf.write(p, arcname=f"BlobFiles/{f_name}")

    os.makedirs("zips", exist_ok=True)
    sh.copy(dat_name, os.path.join("zips", dat_name))
    print(f"Creato {zip_path}")

    return os.path.abspath(zip_path)


# ------------------------------------------------------------------
# 2️⃣  ZIP  +  UPLOAD  su  GCS  (usa config['RUN_ID'] se serve)
# ------------------------------------------------------------------
def zip_and_upload(
    metadata: str,
    *,
    config: dict[str, str],
    run_id: str | None = None,
    tmp_dir: str = "tmp",
    dat_name: str = "DocumentsOfRecord.dat",
    zip_name: str = "solution.zip",
) -> str:
    """
    Crea lo zip e lo carica in:
        gs://<OUTPUT_BUCKET>/<RUN_ID>/solution.zip
    Il RUN_ID può essere passato come argomento
    oppure letto da config['RUN_ID'].
    """
    output_bucket_name = config["OUTPUT_BUCKET"]
    run_id = run_id or config["RUN_ID"]  # <── qui si usa RUN_ID da config se mancante

    # 1) zip
    zip_path = zip_and_export(
        metadata, tmp_dir=tmp_dir, zip_path=zip_name, dat_name=dat_name
    )

    # 2) upload
    storage_client = storage.Client()
    bucket = storage_client.bucket(output_bucket_name)
    blob = bucket.blob(f"{run_id}/{Path(zip_path).name}")

    print(f"Caricamento di '{zip_path}' su gs://{output_bucket_name}/{run_id}/")
    blob.upload_from_filename(zip_path)
    print("Caricamento completato ✔️")

    return f"gs://{output_bucket_name}/{run_id}/{Path(zip_path).name}"

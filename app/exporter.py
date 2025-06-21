import os
import shutil as sh
import zipfile


def is_document(file_path):
    end = file_path.split(".")[-1].upper()
    return end in ["PDF", "JPG", "PNG", "JPEG", "TIFF", "TIF", "JPEG", ".DAT"]


def zip_and_export(metadata: str):
    with open("DocumentsOfRecord.dat", "w", newline="") as f:
        f.write(metadata)
    os.makedirs("zips", exist_ok=True)
    sh.copy("DocumentsOfRecord.dat", "zips/DocumentsOfRecord.dat")
    with zipfile.ZipFile("solution.zip", "w") as zipf:
        for file in os.listdir("tmp"):
            if os.path.isfile(os.path.join("tmp", file)) and is_document(file):
                sh.copy(os.path.join("tmp", file), os.path.join("zips", file))
        zipf.write("BlobFiles/DocumentsOfRecord.dat")

#!/usr/bin/env python3
"""FG G5-05: offline encrypted NVS REVIEW image only, NO device flash/eFuse/write.

This utility ONLY processes user-supplied local private files outside the repo.
It requires an EXISTING matching NVS key partition image. Never creates production keys.
The resulting encrypted image is NOT safe to provision until the full device Flash
Encryption / Secure Boot threat model and manufacturing gates have been approved.
"""
import argparse
import csv
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

SIZE=0x8000
REPO=Path(__file__).resolve().parents[2]

def abort(message):
 raise SystemExit("REFUSED: "+message)

def private_path(value,label):
 p=Path(value).expanduser().resolve(strict=True)
 if p.is_relative_to(REPO):abort(label+" must be outside the Git checkout")
 if not p.is_file():abort(label+" must be a local file")
 return p

def load_ascii(path,max_bytes,label,min_bytes=1):
 data=path.read_bytes()
 if not (min_bytes<=len(data)<=max_bytes):abort(label+" length out of range")
 if any(x<32 or x>126 or x==44 for x in data):
  abort(label+" requires plain ASCII without comma/newline/NUL")
 return data.decode("ascii")

def check_tls(cert_bytes,key_bytes):
 from cryptography import x509
 from cryptography.hazmat.primitives import serialization
 cert_text=cert_bytes.strip()+b"\n"
 key_text=key_bytes.strip()+b"\n"
 if not cert_text.startswith(b"-----BEGIN CERTIFICATE-----"):
  abort("certificate PEM header missing")
 if not key_text.startswith((b"-----BEGIN PRIVATE KEY-----",
                             b"-----BEGIN EC PRIVATE KEY-----",
                             b"-----BEGIN RSA PRIVATE KEY-----")):
  abort("unencrypted private-key PEM required")
 if not (64<len(cert_text)+1<=4096 and 64<len(key_text)+1<=4096):
  abort("certificate/private key too large for fg_net_service.c")
 try:
  cert=x509.load_pem_x509_certificate(cert_text)
  private=serialization.load_pem_private_key(key_text,password=None)
  pub1=cert.public_key().public_bytes(
     encoding=serialization.Encoding.DER,
     format=serialization.PublicFormat.SubjectPublicKeyInfo)
  pub2=private.public_key().public_bytes(
     encoding=serialization.Encoding.DER,
     format=serialization.PublicFormat.SubjectPublicKeyInfo)
  if pub1!=pub2:abort("certificate and private key do not match")
  cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
  now=datetime.now(timezone.utc)
  begin=cert.not_valid_before.replace(tzinfo=timezone.utc)
  end=cert.not_valid_after.replace(tzinfo=timezone.utc)
  if not (begin<=now<end):abort("certificate is expired or not yet valid")
 except (ValueError,TypeError,x509.ExtensionNotFound):
  abort("invalid X.509 certificate, key, or missing SAN")
 return cert_text+b"\x00",key_text+b"\x00"

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--ssid-file",required=True)
 parser.add_argument("--password-file",required=True)
 parser.add_argument("--tls-cert",required=True)
 parser.add_argument("--tls-key",required=True)
 parser.add_argument("--nvs-key-image",required=True)
 parser.add_argument("--idf-generator",required=True)
 parser.add_argument("--output",required=True)
 parser.add_argument("--emit-review-image",action="store_true",
                     help="Explicitly permit local, unapproved offline artifact, NEVER flash")
 args=parser.parse_args(argv)
 if not args.emit_review_image:
  abort("explicit --emit-review-image is mandatory; no production image generation")
 files={
  "SSID":private_path(args.ssid_file,"SSID"),
  "WiFi password":private_path(args.password_file,"WiFi password"),
  "TLS certificate":private_path(args.tls_cert,"TLS certificate"),
  "TLS private key":private_path(args.tls_key,"TLS private key"),
  "NVS keys":private_path(args.nvs_key_image,"NVS keys")
 }
 generator=Path(args.idf_generator).expanduser().resolve(strict=True)
 if not generator.is_file():abort("IDF generator missing")
 out=Path(args.output).expanduser().resolve()
 if out.is_relative_to(REPO):abort("output inside Git checkout is forbidden")
 if not out.parent.is_dir() or out.exists():abort("output directory missing or output exists")
 ssid=load_ascii(files["SSID"],32,"SSID")
 password=load_ascii(files["WiFi password"],63,"WiFi password",8)
 if files["NVS keys"].stat().st_size!=4096:
  abort("NVS key partition image must be exactly 4096 bytes")
 certificate,key=check_tls(files["TLS certificate"].read_bytes(),
                           files["TLS private key"].read_bytes())
 os.umask(0o077)
 with tempfile.TemporaryDirectory(prefix="fg_g505_",dir=str(out.parent)) as td:
  private=Path(td)
  cert_tmp=private/"tls_cert_pem.bin"
  key_tmp=private/"tls_key_pem.bin"
  csv_tmp=private/"secure_fg_cfg.csv"
  cert_tmp.write_bytes(certificate)
  key_tmp.write_bytes(key)
  with csv_tmp.open("w",newline="",encoding="utf-8") as stream:
   writer=csv.writer(stream,lineterminator="\n")
   writer.writerow(["key","type","encoding","value"])
   writer.writerow(["fg_secure_web","namespace","",""])
   writer.writerow(["sta_ssid","data","string",ssid])
   writer.writerow(["sta_pass","data","string",password])
   writer.writerow(["tls_cert","file","binary",str(cert_tmp)])
   writer.writerow(["tls_key","file","binary",str(key_tmp)])
  # A single immutable invocation uses the Espressif reference NVS XTS generator.
  # The subprocess log is hidden because absolute private paths can occur in it.
  cmd=[sys.executable,str(generator),"encrypt",str(csv_tmp),str(out),hex(SIZE),
       "--inputkey",str(files["NVS keys"]),"--outdir",str(out.parent)]
  result=subprocess.run(cmd,check=False,stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
  if result.returncode!=0:abort("Espressif NVS generator failed, output not trusted")
 if not out.is_file() or out.stat().st_size!=SIZE:
  if out.exists():out.unlink()
  abort("encrypted output missing or wrong size")
 out.chmod(0o600)
 print("PASS local encrypted 32768-byte fg_cfg NVS REVIEW artifact; no actual secrets logged")
 print("HOLD no flashing, no eFuse, no operational TLS handshake or production authorization")
 return 0

if __name__=="__main__":
 sys.exit(main())

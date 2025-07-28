@echo off
setlocal enabledelayedexpansion

set CERT_DIR=certs
set CONFIG_PATH=..\openssl.cnf

if not exist %CERT_DIR% (
    mkdir %CERT_DIR%
)
cd %CERT_DIR%

echo 🔐 Certificaten aanmaken (indien nodig)...

:: === CA ===
if not exist ca.pem (
    echo 📜 CA-certificaat maken...
    openssl genrsa -out ca-key.pem 2048
    openssl req -new -x509 -nodes -days 3650 -key ca-key.pem -out ca.pem -config %CONFIG_PATH%
) else (
    echo ✅ CA-bestanden bestaan al. Overslaan.
)

:: === Server ===
if not exist server-cert.pem (
    echo 🖥️ Server-certificaat maken...
    openssl genrsa -out server-key.pem 2048
    openssl req -new -key server-key.pem -out server-req.pem -config %CONFIG_PATH%
    openssl x509 -req -in server-req.pem -days 3650 -CA ca.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem -extensions req_ext -extfile %CONFIG_PATH%
    del server-req.pem
) else (
    echo ✅ Server-certificaten bestaan al. Overslaan.
)

:: === Client ===
if not exist client-cert.pem (
    echo 👤 Client-certificaat maken...
    openssl genrsa -out client-key.pem 2048
    openssl req -new -key client-key.pem -out client-req.pem -config %CONFIG_PATH%
    openssl x509 -req -in client-req.pem -days 3650 -CA ca.pem -CAkey ca-key.pem -set_serial 02 -out client-cert.pem -extensions req_ext -extfile %CONFIG_PATH%
    del client-req.pem
) else (
    echo ✅ Client-certificaten bestaan al. Overslaan.
)

echo ✅ Certificaten klaar in %CERT_DIR%
pause

# PKI (CA y certificado de servidor)

El parcial exige **reutilizar la CA y el certificado de servidor generados en clase**.

1. Antes de `vagrant up`, copie aquí sus archivos de clase con estos nombres:
   - `ca.crt` — certificado de la CA
   - `servidor.crt` — certificado del servidor firmado por la CA
   - `servidor.key` — clave privada del servidor (**no se versiona**, ver `.gitignore`)
2. Si no existen, `scripts/srv2_provision.sh` genera una CA y un certificado equivalentes
   (SAN: `IP:192.168.100.3`, `DNS:srv2-2220335`, `DNS:srv1-2220335`).

Archivos generados en el aprovisionamiento:
- `servidor_fingerprint.txt` — sujeto, emisor, vigencia y huella SHA-256 (punto 7)
- `srv2_hostkeys_fingerprint.txt` — huellas de las claves de host SSH de srv2 (punto 17)

> Si el certificado de clase no incluye `192.168.100.3` en el SAN, `openssl s_client` igual devuelve
> `Verify return code: 0` (no valida el nombre por defecto), pero FileZilla y `lftp` avisarán por desajuste de nombre.

# Capturas Wireshark / tshark (.pcapng)

Generadas desde las VMs con `tshark -w /vagrant/captures/<nombre>.pcapng` y abiertas en Wireshark de Windows.
Están en `.gitignore`; súbalas solo si el docente las solicita.

| Archivo                  | Punto | Filtro de visualización                         |
| :----------------------- | :---: | :----------------------------------------------- |
| `p09_ftp_plano.pcapng` |   9   | `ftp \|\| ftp-data`                              |
| `p09_ftps.pcapng`      |   9   | `tcp.port == 21 \|\| tcp.port in {50000..50010}` |
| `p13_dot_853.pcapng`   |  13  | `tcp.port == 853`                              |
| `p13_dns_53.pcapng`    |  13  | `udp.port == 53`                               |
| `p18_sftp_2222.pcapng` |  18  | `tcp.port == 2222`                             |

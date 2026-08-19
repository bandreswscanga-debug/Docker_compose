# Docker DB — Registro de Aprendices SENA (Flask + MySQL)

Aplicación web desplegada en **AWS EC2** mediante **Docker Compose**, protegida por
**Nginx Proxy Manager** con **HTTPS (Let's Encrypt)** y monitoreada por **Uptime Kuma**
con alertas a **Telegram**.

```
                         INTERNET
                            │
                            ▼
                dockerxxd.duckdns.org
                            │
                            ▼
                       AWS EC2 (3.139.62.238)
                            │
            ┌───────────────┴────────────────┐
            │  Nginx Proxy Manager (80/443)  │
            └───────────────┬────────────────┘
                            │  red Docker interna
              ┌─────────────┴─────────────┐
              │       app-backend:5050    │  Flask (Gunicorn)
              └─────────────┬─────────────┘
                            │
              ┌─────────────┴─────────────┐
              │     servidor-bd:3306      │  MySQL 8.0 (solo interno)
              └───────────────────────────┘
        Otros servicios: uptime-kuma:3001, proxy-manager:81, portainer (localhost)
```

## 1. URLs

| Recurso | URL |
|---|---|
| Aplicación (HTTP) | http://dockerxxd.duckdns.org |
| Aplicación (HTTPS) | https://dockerxxd.duckdns.org |
| Panel Nginx Proxy Manager | http://3.139.62.238:81 |
| Panel Uptime Kuma | http://3.139.62.238:3001 |
| Portainer (solo túnel SSH) | http://127.0.0.1:9000 |

## 2. Arquitectura

- **proxy-manager**: Nginx Proxy Manager (jc21/nginx-proxy-manager) — puertos 80, 443, 81.
- **app-backend**: Flask servido por Gunicorn en el puerto interno 5050 (no expuesto).
- **servidor-bd**: MySQL 8.0 en el puerto interno 3306 (no expuesto a Internet).
- **uptime-kuma**: Monitoreo con 3 monitores y notificación Telegram (puerto 3001).
- **portainer**: Panel de gestión Docker (solo localhost/túnel SSH).

Todos los servicios comparten la red Docker `red-cba`, por lo que NPM alcanza la
aplicación como `app-backend:5050` (sin pasar por la IP pública).

## 3. Requisitos

- Ubuntu Server 22.04+ (24.04/26.04) en EC2.
- Docker Engine + Docker Compose v2.
- Dominio DuckDNS `dockerxxd.duckdns.org` apuntando a la IP pública de EC2.
- Instancia con al menos 1 GB RAM (recomendado: `t3.micro` con swap de 2 GB).

## 4. Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/bandreswscanga-debug/Docker_compose.git
cd Docker_compose

# 2. Configurar variables de entorno
cp .env.example .env
nano .env        # pon tus valores reales

# 3. Construir y levantar
docker compose build
docker compose up -d
```

## 5. Variables de entorno (`.env`)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `APP_ENV` | Entorno de la app | `production` |
| `APP_PORT` | Puerto interno de Flask | `5050` |
| `DB_HOST` | Nombre del servicio MySQL (NO localhost) | `servidor-bd` |
| `DB_PORT` | Puerto MySQL | `3306` |
| `DB_NAME` | Base de datos | `adso_db` |
| `DB_USER` | Usuario MySQL | `adso_user` |
| `DB_PASSWORD` | Contraseña MySQL | `******` |
| `MYSQL_ROOT_PASSWORD` | Password root de MySQL | `******` |
| `MYSQL_DATABASE` | BD que crea el contenedor | `adso_db` |
| `MYSQL_USER` | Usuario que crea el contenedor | `adso_user` |
| `MYSQL_PASSWORD` | Password del usuario | `******` |

> **Nunca** subas `.env` al repositorio. Usa `.env.example` como plantilla sin secretos.

## 6. Docker

```bash
docker compose up -d          # levantar todo
docker compose down           # detener (conserva volúmenes/datos)
docker compose down -v        # ⚠️ ELIMINA VOLÚMENES (no usar en pruebas normales)
docker compose logs --tail=100
docker compose ps
```

## 7. Base de datos

- MySQL 8.0, volumen nombrado `mysql-data` (persistente).
- El puerto 3306 **NO** se publica: solo se accede por la red Docker interna
  (`servidor-bd:3306`).
- Config de memoria para instancias pequeñas en `mysql/conf.d/my.cnf`
  (performance_schema OFF, buffer pool 64M).

## 8. AWS EC2

- Región `us-east-2`, tipo `t3.micro`, Ubuntu.
- Se recomienda asociar una **Elastic IP** a la instancia para que la IP pública
  (`3.139.62.238`) no cambie entre reinicios/paradas, evitando tener que
  actualizar DuckDNS cada vez.

## 9. Security Groups (launch-wizard-1)

| Puerto | Protocolo | Origen | Uso |
|---|---|---|---|
| 22 | TCP | Tu IP | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP (NPM) |
| 443 | TCP | 0.0.0.0/0 | HTTPS (NPM) |
| 81 | TCP | Tu IP | Panel NPM (no público) |
| 3001 | TCP | Tu IP | Uptime Kuma (no público) |
| 3306 | TCP | — | **NO abrir** |
| 5050 | TCP | — | **NO abrir** |
| 9000 | TCP | — | **NO abrir** |

## 10. DuckDNS

Actualiza la IP (cron sugerido en el servidor):

```bash
# Una vez
curl -s "https://www.duckdns.org/update?domains=dockerxxd&token=TU_TOKEN&ip="

# Verificación
dig +short dockerxxd.duckdns.org
nslookup dockerxxd.duckdns.org
```

> El token es personal y no debe subirse al repositorio.

## 11. Nginx Proxy Manager

En el panel (puerto 81) se creó el Proxy Host:

```
Domain Names:  dockerxxd.duckdns.org
Scheme:        http
Forward Host:  app-backend      ← nombre del servicio Docker (NO la IP pública)
Forward Port:  5050
SSL:           Let's Encrypt (Force SSL ON, HTTP/2 ON)
```

NPM y la app están en la misma red Docker, por eso el destino es el nombre del
servicio (`app-backend:5050`) y no `3.139.62.238:5051` (como estaba antes).

## 12. HTTPS / Let's Encrypt

- Certificado emitido por Let's Encrypt para `dockerxxd.duckdns.org`
  (renovación automática por NPM).
- HTTP redirige a HTTPS (301).
- Verificación:

```bash
curl -I https://dockerxxd.duckdns.org
echo | openssl s_client -connect dockerxxd.duckdns.org:443 -servername dockerxxd.duckdns.org 2>/dev/null | openssl x509 -noout -dates
```

## 13. Uptime Kuma + Telegram

- Panel: `http://3.139.62.238:3001` (usuario `admin`).
- Monitores:
  1. **API Backend HTTPS** — `https://dockerxxd.duckdns.org/api/aprendices` (status 200).
  2. **Base de Datos MySQL** — conexión MySQL a `servidor-bd:3306`.
  3. **Servidor Cloud** — TCP `3.139.62.238:443`.
- Notificación **Telegram** (bot `@Dockerxxd_alerts_bot`): alertas de caída y
  recuperación. Configurada en *Settings → Notifications*.

## 14. Comandos de mantenimiento

```bash
docker stats                         # uso de CPU/RAM en vivo
docker ps                            # contenedores activos
docker compose logs --tail=100       # logs de todos los servicios
docker compose logs -f app-backend   # logs en tiempo real de la app
sudo ss -lntp                        # puertos en escucha
sudo journalctl -u docker --since "1 hour ago"   # logs del demonio Docker
```

## 15. Solución de problemas

- **Contenedor unhealthy**: revisa `docker logs <contenedor>`.
- **502 en el dominio**: la app no responde; verifica `docker ps` y la salud de
  `app-backend`.
- **El monitor de MySQL en DOWN**: el contenedor MySQL no acepta conexiones;
  revisa `docker logs servidor-bd`.
- **No llegan alertas a Telegram**: el usuario debe haber iniciado el bot con
  `/start`, y el `Chat ID` debe ser el correcto.
- **OOM (RAM 1 GB)**: el swap de 2 GB ya está configurado en `/etc/fstab`;
  verifica con `free -h`.

## 16. Reiniciar todo

```bash
docker compose down
docker compose up -d
```

## 17. Backups

```bash
# Base de datos (dump SQL)
docker exec servidor-bd sh -c 'exec mysqldump -uadso_user -p"$MYSQL_PASSWORD" adso_db' > backup_db_$(date +%F).sql

# Configuración (archivos clave)
tar -czf docker_config_$(date +%F).tar.gz docker-compose.yml .env mysql/

# Restaurar BD
docker exec -i servidor-bd sh -c 'exec mysql -uadso_user -p"$MYSQL_PASSWORD" adso_db' < backup_db_FECHA.sql
```

## 18. Actualizar la aplicación

```bash
git pull                        # traer el código nuevo
docker compose build app-backend
docker compose up -d app-backend
```

#!/bin/bash
set -e

echo "=========================================="
echo "  DEMO CI/CD - 3 pushes automaticos"
echo "=========================================="
echo ""

# --- PASO 1: Push con pipeline VERDE ---
echo "[1/3] Push pipeline FUNCIONAL (verde)..."
# Asegurar que test_app.py esta en su version correcta
cat > test_app.py << 'PYEOF'
import pytest
from unittest.mock import patch, MagicMock
from sample_app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_returns_200(client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("sample_app.get_db_connection", return_value=mock_conn):
        response = client.get("/")
        assert response.status_code == 200


def test_api_aprendices_returns_json(client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("sample_app.get_db_connection", return_value=mock_conn):
        response = client.get("/api/aprendices")
        assert response.status_code == 200
        assert response.content_type == "application/json"


def test_api_registrar_campos_faltantes(client):
    response = client.post(
        "/api/registrar",
        json={"nombre_completo": "", "numero_documento": "", "ficha": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_registrar_exitoso(client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("sample_app.get_db_connection", return_value=mock_conn):
        response = client.post(
            "/api/registrar",
            json={
                "nombre_completo": "Juan Perez",
                "numero_documento": "12345678",
                "ficha": "2471168",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "mensaje" in data


def test_api_registrar_sin_json(client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("sample_app.get_db_connection", return_value=mock_conn):
        response = client.post(
            "/api/registrar",
            data="",
            content_type="application/json",
        )
        assert response.status_code == 400
PYEOF

git add test_app.py .github/workflows/deploy.yml requirements.txt
git commit -m "feat: add unit tests and CI/CD pipeline with 2 jobs" --allow-empty
git push origin main
echo "[OK] Push verde enviado. Espera ~1 min en GitHub Actions."
echo ""
echo ">>> CAPTURA PANTALLA AHORA: Actions > workflow en VERDE con 2 jobs <<<
echo ""

read -p "Presiona ENTER despues de capturar la pantalla verde..."

# --- PASO 2: Push con test FALLIDO (rojo) ---
echo "[2/3] Push con test FORZADO a fallar (rojo)..."
sed -i 's/assert response.status_code == 200/assert response.status_code == 500  # FORCED FAILURE/' test_app.py
git add test_app.py
git commit -m "demo: force test failure for fail-fast demonstration"
git push origin main
echo "[OK] Push rojo enviado. El pipeline DEBE fallar en Tests."
echo ""
echo ">>> CAPTURA PANTALLA AHORA: Actions > workflow en ROJO (solo Tests fallo) <<<
echo ""

read -p "Presiona ENTER despues de capturar la pantalla roja..."

# --- PASO 3: Revertir el fallo (pipeline vuelve a verde) ---
echo "[3/3] Revirtiendo cambio para dejar pipeline funcional..."
git checkout -- test_app.py
git add test_app.py
git commit -m "fix: revert forced failure, restore passing tests"
git push origin main
echo "[OK] Pipeline restaurado."
echo ""
echo "=========================================="
echo "  LISTO. Ahora solo te falta:"
echo "  1. Capturar la Estructura del Repo"
echo "  2. Capturar la URL en produccion"
echo "  3. Unir las 4 capturas en un PDF"
echo "=========================================="

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
        assert response.status_code == 500  # FORZAR FALLO PARA DEMO


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

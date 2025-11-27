import pytest


class TestLaunchProbe:
    """Tests for the POST /probes endpoint."""

    def test_launch_probe_returns_201(self, client):
        response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        assert response.status_code == 201

    def test_launch_probe_returns_correct_initial_position(self, client):
        response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        data = response.json()
        assert data["x"] == 0
        assert data["y"] == 0
        assert data["direction"] == "NORTH"
        assert "id" in data

    def test_launch_probe_with_different_direction(self, client):
        response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "EAST"},
        )
        data = response.json()
        assert data["direction"] == "EAST"

    def test_launch_probe_with_invalid_direction_returns_422(self, client):
        response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "INVALID"},
        )
        assert response.status_code == 422

    def test_launch_probe_with_negative_coordinates_returns_422(self, client):
        response = client.post(
            "/probes",
            json={"x": -1, "y": 5, "direction": "NORTH"},
        )
        assert response.status_code == 422


class TestMoveProbe:
    """Tests for the PUT /probes/{id}/commands endpoint."""

    def test_move_probe_with_valid_commands(self, client):
        # Primeiro lança a sonda
        launch_response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        probe_id = launch_response.json()["id"]

        # Depois move
        response = client.put(
            f"/probes/{probe_id}/commands",
            json={"commands": "MRM"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["x"] == 1
        assert data["y"] == 1
        assert data["direction"] == "EAST"

    def test_move_probe_with_complex_sequence(self, client):
        launch_response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        probe_id = launch_response.json()["id"]

        response = client.put(
            f"/probes/{probe_id}/commands",
            json={"commands": "MMRMMRMRRM"},
        )
        data = response.json()
        assert data["x"] == 2
        assert data["y"] == 2
        assert data["direction"] == "NORTH"

    def test_move_probe_not_found_returns_404(self, client):
        response = client.put(
            "/probes/nonexistent/commands",
            json={"commands": "M"},
        )
        assert response.status_code == 404

    def test_move_probe_with_invalid_commands_returns_422(self, client):
        launch_response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        probe_id = launch_response.json()["id"]

        # Comandos inválidos no schema (regex não permite X)
        response = client.put(
            f"/probes/{probe_id}/commands",
            json={"commands": "MXM"},
        )
        assert response.status_code == 422

    def test_move_probe_out_of_bounds_returns_400(self, client):
        launch_response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        probe_id = launch_response.json()["id"]

        # Tenta mover para sul quando está em y=0
        response = client.put(
            f"/probes/{probe_id}/commands",
            json={"commands": "LLM"},  # Vira para sul e tenta mover
        )
        assert response.status_code == 400


class TestListProbes:
    """Tests for the GET /probes endpoint."""

    def test_list_probes_empty(self, client):
        response = client.get("/probes")
        assert response.status_code == 200
        data = response.json()
        assert data["probes"] == []

    def test_list_probes_after_launch(self, client):
        # Lança uma sonda
        client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )

        response = client.get("/probes")
        data = response.json()
        assert len(data["probes"]) == 1
        assert data["probes"][0]["x"] == 0
        assert data["probes"][0]["y"] == 0

    def test_list_multiple_probes(self, client):
        # Lança duas sondas
        client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        client.post(
            "/probes",
            json={"x": 3, "y": 3, "direction": "EAST"},
        )

        response = client.get("/probes")
        data = response.json()
        assert len(data["probes"]) == 2

    def test_list_probes_shows_updated_position(self, client):
        # Lança e move uma sonda
        launch_response = client.post(
            "/probes",
            json={"x": 5, "y": 5, "direction": "NORTH"},
        )
        probe_id = launch_response.json()["id"]

        client.put(
            f"/probes/{probe_id}/commands",
            json={"commands": "MRM"},
        )

        response = client.get("/probes")
        data = response.json()
        probe = data["probes"][0]
        assert probe["x"] == 1
        assert probe["y"] == 1
        assert probe["direction"] == "EAST"


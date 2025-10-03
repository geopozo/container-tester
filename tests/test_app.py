from unittest.mock import MagicMock

import pytest
from docker import DockerClient
from docker.errors import ImageNotFound

from container_tester import app

IMAGE_TAG = "test_image"


@pytest.fixture
def mock_client():
    client = MagicMock(spec=DockerClient)
    client.containers.list.return_value = []
    client.images.list.return_value = []
    return client


class TestApp:
    def test_docker_client_returns_instance(self, mock_client):
        assert isinstance(mock_client, DockerClient)
        assert mock_client.containers.list() == []

    def test_docker_client_raises_exception_if_docker_not_running(self):
        with pytest.raises(SystemExit) as e:
            app.docker_client()
        assert e.value.code == 1

    def test_remove_dockerfile_removes_file(self, tmp_path):
        docker_file = tmp_path / f"Dockerfile.{IMAGE_TAG}"
        docker_file.write_text("content")

        app.remove_dockerfile(IMAGE_TAG, str(tmp_path))

        assert not docker_file.exists()

    def test_remove_image_handles_image_not_found(self, mock_client, capsys):
        mock_client.images.remove.side_effect = ImageNotFound("not found")

        app.remove_image(mock_client, IMAGE_TAG)

        captured = capsys.readouterr()
        assert f"Image '{IMAGE_TAG}' not found" in captured.out

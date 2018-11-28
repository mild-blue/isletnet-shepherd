from unittest import mock
import pytest
import asyncio

from shepherd.api import create_app
from shepherd.api.swagger import swagger
from shepherd.api.models import SheepModel
from shepherd.api.views import create_shepherd_routes
from shepherd.shepherd import Shepherd


@pytest.fixture(scope="function")
def mock_shepherd():
    def status_gen():
        yield "bare_sheep", SheepModel({
                "running": False,
                "model": {
                    "name": "model_1",
                    "version": "latest"
                }
            })

    def ready(*args):
        return args[0] == 'uuid-ready'

    async def nothing(*args, **kwargs):
        return None

    m = mock.create_autospec(Shepherd)
    m.get_status.side_effect = status_gen
    m.is_job_done.side_effect = ready
    m.job_done_condition = asyncio.Condition()
    m.enqueue_job.side_effect = nothing
    yield m


@pytest.fixture(scope="function")
def app(minio, mock_shepherd):
    app = create_app(debug=True)
    app.add_routes(create_shepherd_routes(mock_shepherd, minio))
    swagger.init_app(app)

    yield app

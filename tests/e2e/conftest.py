from threading import Thread

import pytest
from werkzeug.serving import make_server

from shop import create_app


@pytest.fixture(scope="session")
def base_url():
    with make_server("127.0.0.1", 0, create_app()) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            thread.join()

import os
import sys
import time
import pytest
import subprocess
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent_dir, "client", "src"))
sys.path.insert(0, parent_dir)

from gemini_explainer_client import ExplainerClient
from database import get_session, User, Upload

BASE_DIR = Path(__file__).parent.parent
API_DIR = BASE_DIR / "api"
EXPLAINER_DIR = BASE_DIR / "explainer"
SAMPLE_PPTX = BASE_DIR / "gemini-explainer" / "KidSafe.pptx"

API_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def setup_database():
    """Initialize the database before tests."""
    from database import create_tables
    create_tables()


@pytest.fixture(scope="session")
def api_server(setup_database):
    """Start the Flask API server for the duration of the tests."""
    process = subprocess.Popen(
        ["python", "app.py"],
        cwd=API_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    yield process
    process.terminate()
    process.wait()


@pytest.fixture(scope="session")
def explainer_service(setup_database):
    """Start the Explainer service for the duration of the tests."""
    process = subprocess.Popen(
        ["python", "explainer_service.py"],
        cwd=EXPLAINER_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    yield process
    process.terminate()
    process.wait()


@pytest.fixture
def client():
    """Create a client instance."""
    return ExplainerClient(base_url=API_URL)


def test_upload_returns_uid(api_server, client):
    """Test that the upload method returns a UID."""
    uid = client.upload(str(SAMPLE_PPTX))
    assert uid, "No UID returned from upload"
    assert isinstance(uid, str), "UID is not a string"


def test_upload_with_email(api_server, client):
    """Test that the upload method works with email."""
    test_email = "test@example.com"
    uid = client.upload(str(SAMPLE_PPTX), email=test_email)
    assert uid, "No UID returned from upload with email"
    assert isinstance(uid, str), "UID is not a string"


def test_status_after_upload(api_server, client):
    """Test that the status method returns correct status after upload."""
    uid = client.upload(str(SAMPLE_PPTX))
    status = client.status(uid)
    assert status.status in ['uploaded', 'processing', 'completed'], f"Unexpected status: {status.status}"
    assert status.uid == uid, "UID mismatch in status response"


def test_status_by_email_filename(api_server, client):
    """Test status check by email and filename."""
    test_email = "test2@example.com"
    filename = "KidSafe.pptx"

    uid = client.upload(str(SAMPLE_PPTX), email=test_email)

    status = client.status_by_email_filename(test_email, filename)
    assert status.uid == uid, "UID mismatch when checking by email/filename"
    assert status.filename == filename, "Filename mismatch"


def test_explainer_processes_files(api_server, explainer_service, client):
    """Test that the Explainer processes files and returns completed status."""
    uid = client.upload(str(SAMPLE_PPTX))

    start_time = time.time()
    while time.time() - start_time < 60:
        status = client.status(uid)
        if status.is_done():
            break
        time.sleep(5)

    assert status.is_done(), "File was not processed within timeout"
    assert status.explanation is not None, "No explanation returned for processed file"


def test_nonexistent_uid(api_server, client):
    """Test that requesting a non-existent UID returns 'not found' status."""
    status = client.status("nonexistent_uid")
    assert status.is_not_found(), f"Unexpected status for non-existent UID: {status.status}"


def test_database_integration():
    """Test that data is properly stored in the database."""
    session = get_session()
    try:
        uploads = session.query(Upload).all()
        assert len(uploads) > 0, "No uploads found in database"

        test_user = session.query(User).filter(User.email == "test@example.com").first()
        if test_user:
            assert len(test_user.uploads) > 0, "User should have uploads"
    finally:
        session.close()


if __name__ == "__main__":
    """Run the end-to-end test manually."""
    from database import create_tables

    print("Initializing database...")
    create_tables()

    print("Starting the Web API...")
    api_process = subprocess.Popen(
        ["python", "app.py"],
        cwd=API_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("Starting the Explainer service...")
    explainer_process = subprocess.Popen(
        ["python", "explainer_service.py"],
        cwd=EXPLAINER_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        time.sleep(5)

        print("Creating client...")
        client = ExplainerClient(base_url=API_URL)

        print(f"Uploading file: {SAMPLE_PPTX}")
        uid = client.upload(str(SAMPLE_PPTX))
        print(f"Uploaded file with UID: {uid}")

        print("Uploading file with email...")
        uid_with_email = client.upload(str(SAMPLE_PPTX), email="test@example.com")
        print(f"Uploaded file with email, UID: {uid_with_email}")

        print("Checking status by UID...")
        status = client.status(uid)
        print(f"Status: {status.status}")

        print("Checking status by email/filename...")
        status_by_email = client.status_by_email_filename("test@example.com", "KidSafe.pptx")
        print(f"Status by email: {status_by_email.status}, UID: {status_by_email.uid}")

        print("Waiting for processing to complete...")
        start_time = time.time()
        while time.time() - start_time < 60:
            status = client.status(uid)
            if status.is_done():
                break
            print(f"Still processing... Status: {status.status}")
            time.sleep(5)

        if status.is_done():
            print("Processing complete!")
            print(f"Number of slides explained: {len(status.explanation)}")
        else:
            print(f"Processing result: {status.status}")
            if status.error_message:
                print(f"Error: {status.error_message}")

    except Exception as e:
        print(f"Error during test: {e}")

    finally:
        print("Terminating services...")
        api_process.terminate()
        explainer_process.terminate()
        api_process.wait()
        explainer_process.wait()


@pytest.fixture(scope="session")
def explainer_service():
    """Start the Explainer service for the duration of the tests."""
    process = subprocess.Popen(
        ["python", "explainer_service.py"],
        cwd=EXPLAINER_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    yield process
    process.terminate()
    process.wait()


@pytest.fixture
def client():
    """Create a client instance."""
    return ExplainerClient(base_url=API_URL)


def test_upload_returns_uid(api_server, client):
    """Test that the upload method returns a UID."""
    uid = client.upload(str(SAMPLE_PPTX))
    assert uid, "No UID returned from upload"
    assert isinstance(uid, str), "UID is not a string"


def test_status_after_upload(api_server, client):
    """Test that the status method returns pending or done after upload."""
    uid = client.upload(str(SAMPLE_PPTX))
    status = client.status(uid)
    assert status.status in ['pending', 'done'], f"Unexpected status: {status.status}"


def test_explainer_processes_files(api_server, explainer_service, client):
    """Test that the Explainer processes files and returns done status."""
    uid = client.upload(str(SAMPLE_PPTX))

    start_time = time.time()
    while time.time() - start_time < 60:
        status = client.status(uid)
        if status.is_done():
            break
        time.sleep(5)

    assert status.is_done(), "File was not processed within timeout"
    assert status.explanation is not None, "No explanation returned for processed file"


def test_nonexistent_uid(api_server, client):
    """Test that requesting a non-existent UID returns 'not found' status."""
    status = client.status("nonexistent_uid")
    assert status.is_not_found(), f"Unexpected status for non-existent UID: {status.status}"


if __name__ == "__main__":
    """Run the end-to-end test manually."""
    print("Starting the Web API...")
    api_process = subprocess.Popen(
        ["python", "app.py"],
        cwd=API_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("Starting the Explainer service...")
    explainer_process = subprocess.Popen(
        ["python", "explainer_service.py"],
        cwd=EXPLAINER_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        time.sleep(5)

        print("Creating client...")
        client = ExplainerClient(base_url=API_URL)

        print(f"Uploading file: {SAMPLE_PPTX}")
        uid = client.upload(str(SAMPLE_PPTX))
        print(f"Uploaded file with UID: {uid}")

        print("Checking status...")
        status = client.status(uid)
        print(f"Initial status: {status.status}")

        print("Waiting for processing to complete...")
        start_time = time.time()
        while time.time() - start_time < 60:
            status = client.status(uid)
            if status.is_done():
                break
            print("Still processing...")
            time.sleep(5)

        if status.is_done():
            print("Processing complete!")
            print(f"Number of slides explained: {len(status.explanation)}")
        else:
            print("Processing timed out.")

    except Exception as e:
        print(f"Error during test: {e}")

    finally:
        print("Terminating services...")
        api_process.terminate()
        explainer_process.terminate()
        api_process.wait()
        explainer_process.wait()
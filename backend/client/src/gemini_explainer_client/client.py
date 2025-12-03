import os
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


class ExplainerClientError(Exception):
    """Exception raised for errors in the Explainer client."""

    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


@dataclass
class Status:
    """Representation of a file processing status."""
    status: str
    uid: Optional[str]
    filename: Optional[str]
    upload_time: Optional[str]
    finish_time: Optional[str]
    explanation: Optional[List[Dict[str, Any]]]
    error_message: Optional[str] = None

    def __post_init__(self):
        """Convert timestamp strings to datetime objects if available."""
        if self.upload_time:
            try:
                self.upload_time = datetime.fromisoformat(self.upload_time.replace('Z', '+00:00'))
            except ValueError:
                pass

        if self.finish_time:
            try:
                self.finish_time = datetime.fromisoformat(self.finish_time.replace('Z', '+00:00'))
            except ValueError:
                pass

    def is_done(self) -> bool:
        """Check if the processing is done."""
        return self.status == 'completed'

    def is_pending(self) -> bool:
        """Check if the processing is still pending."""
        return self.status in ['uploaded', 'processing']

    def is_not_found(self) -> bool:
        """Check if the file was not found."""
        return self.status == 'not found'

    def is_failed(self) -> bool:
        """Check if the processing failed."""
        return self.status == 'failed'


class ExplainerClient:
    """Client for interacting with the Gemini Explainer Web API."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the client with the API base URL.
        """
        self.base_url = base_url.rstrip('/')

    def upload(self, file_path: str, email: Optional[str] = None) -> str:
        """
        Upload a PowerPoint file to the Explainer API.
        """
        if not os.path.exists(file_path):
            raise ExplainerClientError(f"File not found: {file_path}")

        if not file_path.lower().endswith('.pptx'):
            raise ExplainerClientError(f"File is not a PowerPoint file: {file_path}")

        try:
            files = {'file': open(file_path, 'rb')}
            data = {}

            if email:
                data['email'] = email

            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                data=data
            )

            files['file'].close()
            response.raise_for_status()

            response_data = response.json()
            return response_data['uid']

        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            response_text = e.response.text if hasattr(e, 'response') else None

            raise ExplainerClientError(
                f"Error uploading file: {str(e)}",
                status_code=status_code,
                response=response_text
            )

    def status(self, uid: str) -> Status:
        """
        Check the status of a file processing by UID.
        """
        try:
            response = requests.get(f"{self.base_url}/status/{uid}")
            response.raise_for_status()

            data = response.json()

            return Status(
                status=data['status'],
                uid=data.get('uid'),
                filename=data.get('filename'),
                upload_time=data.get('upload_time'),
                finish_time=data.get('finish_time'),
                explanation=data.get('explanation'),
                error_message=data.get('error_message')
            )

        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None

            if status_code == 404:
                return Status(
                    status='not found',
                    uid=None,
                    filename=None,
                    upload_time=None,
                    finish_time=None,
                    explanation=None
                )

            response_text = e.response.text if hasattr(e, 'response') else None

            raise ExplainerClientError(
                f"Error checking status: {str(e)}",
                status_code=status_code,
                response=response_text
            )

    def status_by_email_filename(self, email: str, filename: str) -> Status:
        """
        Check the status of the latest upload by email and filename.
        """
        try:
            response = requests.get(
                f"{self.base_url}/status",
                params={'email': email, 'filename': filename}
            )
            response.raise_for_status()

            data = response.json()

            return Status(
                status=data['status'],
                uid=data.get('uid'),
                filename=data.get('filename'),
                upload_time=data.get('upload_time'),
                finish_time=data.get('finish_time'),
                explanation=data.get('explanation'),
                error_message=data.get('error_message')
            )

        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None

            if status_code == 404:
                return Status(
                    status='not found',
                    uid=None,
                    filename=filename,
                    upload_time=None,
                    finish_time=None,
                    explanation=None
                )

            response_text = e.response.text if hasattr(e, 'response') else None

            raise ExplainerClientError(
                f"Error checking status by email/filename: {str(e)}",
                status_code=status_code,
                response=response_text
            )

    def history(self, email: str) -> Dict[str, Any]:
        """
        Get upload history for a user by email.
        """
        try:
            response = requests.get(
                f"{self.base_url}/history",
                params={'email': email}
            )
            response.raise_for_status()

            data = response.json()
            return data

        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            response_text = e.response.text if hasattr(e, 'response') else None

            raise ExplainerClientError(
                f"Error getting upload history: {str(e)}",
                status_code=status_code,
                response=response_text
            )
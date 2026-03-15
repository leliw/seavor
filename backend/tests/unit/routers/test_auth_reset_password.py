import re
from typing import Optional

from ampf.testing import ApiTestClient
import pytest
from ampf.auth import AuthService
from ampf.base import BaseEmailSender, EmailTemplate
from dependencies import get_auth_service
from fastapi import FastAPI

from app.app_state import AppState


class TestEmailSender(BaseEmailSender):
    """A test email sender that stores sent emails in memory."""

    def __init__(self):
        self.sent_emails = []

    def send(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
    ) -> None:
        self.sent_emails.append(
            {
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "attachment_path": attachment_path,
            }
        )


@pytest.fixture
def email_sender():
    """Return an instance of the test email sender."""
    return TestEmailSender()


def auth_service(app_state: AppState, email_sender) -> AuthService:
    reset_mail_template = EmailTemplate(
        sender=app_state.config.reset_password_mail.sender,
        subject=app_state.config.reset_password_mail.subject,
        body_template=app_state.config.reset_password_mail.body_template,
    )
    return AuthService(
        storage_factory=app_state.factory,
        user_service=app_state.user_service,
        auth_config=app_state.config.auth,
        email_sender_service=email_sender,
        reset_mail_template=reset_mail_template,
    )


@pytest.fixture
def client(app: FastAPI, email_sender):
    with ApiTestClient(app) as client:
        app.dependency_overrides[get_auth_service] = lambda: auth_service(app.state.app_state, email_sender)
        yield client


@pytest.mark.asyncio
async def test_reset_password_request(email_sender, client):
    # Given: Stored an user with email
    # await user_service.create(User(email="test@test.com", password="test"))
    # When: The user requests password reset
    response = client.post(
        "/api/reset-password-request",
        json={"email": "test@test.com"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    # Then: Email was sent
    assert len(email_sender.sent_emails) == 1
    email = email_sender.sent_emails[0]
    assert email["recipient"] == "test@test.com"
    match = re.search(r"please enter the following code into the form: (\S+)\.", email["body"])
    code = match.group(1) if match else ""
    assert len(code) == 16
    match = re.search(r"This code is valid for (\d+) minutes\.", email["body"])
    time = match.group(1) if match else None
    assert time == "15"


@pytest.mark.asyncio
async def test_reset_password(email_sender, client):
    # Given: Stored an user with email
    # await user_service.create(User(email="test@test.com", password="test"))
    # Given: The user requests password reset
    client.post(
        "/api/reset-password-request",
        json={"email": "test@test.com"},
    )
    # Given: Code is extracted from email
    assert len(email_sender.sent_emails) == 1
    email = email_sender.sent_emails[0]
    match = re.search(r"please enter the following code into the form: (\S+)\.", email["body"])
    code = match.group(1) if match else None
    # When: Default user resets password with the code
    response = client.post(
        "/api/reset-password",
        json={"email": "test@test.com", "reset_code": code, "new_password": "new_test"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    # Then: Default user logs in with new password
    response = client.post(
        "/api/login",
        data={"username": "test", "password": "new_test"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200

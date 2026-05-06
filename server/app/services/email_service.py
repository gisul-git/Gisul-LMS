from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmailService:
    def __init__(self) -> None:
        self._client = SendGridAPIClient(settings.sendgrid_api_key)

    async def send_verification_email(self, to_email: str, full_name: str, token: str) -> None:
        verify_url = f"{settings.frontend_url}/verify-email?token={token}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Verify Your Email Address</h2>
            <p>Hi {full_name},</p>
            <p>Thank you for registering. Please verify your email address by clicking the button below.</p>
            <p>This link expires in {settings.email_verification_expire_hours} hours.</p>
            <a href="{verify_url}"
               style="display:inline-block;padding:12px 24px;background:#4F46E5;color:#fff;
                      text-decoration:none;border-radius:6px;font-weight:bold;">
                Verify Email
            </a>
            <p style="margin-top:20px;color:#6B7280;font-size:14px;">
                If you did not create an account, you can safely ignore this email.
            </p>
        </div>
        """
        await self._send(to_email, "Verify your email address", html_content)

    async def send_password_reset_email(self, to_email: str, full_name: str, token: str) -> None:
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Reset Your Password</h2>
            <p>Hi {full_name},</p>
            <p>We received a request to reset your password. Click the button below to proceed.</p>
            <p>This link expires in 1 hour.</p>
            <a href="{reset_url}"
               style="display:inline-block;padding:12px 24px;background:#DC2626;color:#fff;
                      text-decoration:none;border-radius:6px;font-weight:bold;">
                Reset Password
            </a>
            <p style="margin-top:20px;color:#6B7280;font-size:14px;">
                If you did not request a password reset, please ignore this email.
            </p>
        </div>
        """
        await self._send(to_email, "Reset your password", html_content)

    async def _send(self, to_email: str, subject: str, html_content: str) -> None:
        message = Mail(
            from_email=(settings.sendgrid_from_email, settings.sendgrid_from_name),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        try:
            # SendGrid client is sync — run in thread pool in production
            # For now, direct call (acceptable for email dispatch)
            response = self._client.send(message)
            logger.info(
                "email_sent",
                to=to_email,
                subject=subject,
                status=response.status_code,
            )
        except Exception as exc:
            logger.error("email_send_failed", to=to_email, error=str(exc))
            # Don't raise — email failure should not break auth flow

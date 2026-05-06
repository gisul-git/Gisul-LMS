from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"


# Cookie names
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"

# Header names
CORRELATION_ID_HEADER = "X-Correlation-ID"

# Password policy
PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-#^])[A-Za-z\d@$!%*?&_\-#^]{8,}$"

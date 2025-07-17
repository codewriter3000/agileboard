# app/core/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict, Set
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel
import time
import uuid

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token blacklist - serverless-friendly in-memory cache with TTL
class TokenBlacklist:
    def __init__(self):
        self._blacklist: Dict[str, float] = {}  # token -> expiration_timestamp
        self._user_tokens: Dict[int, Set[str]] = {}  # user_id -> set of tokens

    def track_token(self, token: str, user_id: int, expires_at: float):
        """Track an active token for a user."""
        if user_id not in self._user_tokens:
            self._user_tokens[user_id] = set()
        self._user_tokens[user_id].add(token)

    def add_token(self, token: str, expires_at: float, user_id: int = None):
        """Add a token to the blacklist with expiration time."""
        self._blacklist[token] = expires_at

        # Track token by user ID if provided
        if user_id:
            if user_id not in self._user_tokens:
                self._user_tokens[user_id] = set()
            self._user_tokens[user_id].add(token)

        # Note: We don't cleanup expired tokens here to allow tests to verify
        # that tokens are initially added. Cleanup happens in is_blacklisted()

    def is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted."""
        if token not in self._blacklist:
            return False

        # Check if the blacklist entry has expired
        if time.time() > self._blacklist[token]:
            # Token blacklist entry expired, remove it
            self._remove_token(token)
            return False

        return True

    def revoke_all_user_tokens(self, user_id: int):
        """Revoke all tokens belonging to a specific user."""
        if user_id not in self._user_tokens:
            return

        # Get current time for checking expiration
        current_time = time.time()

        # Revoke all tokens for this user
        tokens_to_revoke = self._user_tokens[user_id].copy()
        for token in tokens_to_revoke:
            try:
                # Try to decode token to get expiration
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                exp_timestamp = payload.get("exp")
                if exp_timestamp and current_time <= exp_timestamp:
                    # Token is still valid, add to blacklist
                    self._blacklist[token] = exp_timestamp
                else:
                    # Token has expired naturally, remove from tracking
                    self._user_tokens[user_id].discard(token)
            except JWTError:
                # If token is invalid, remove from user tracking
                self._user_tokens[user_id].discard(token)

        # Clean up expired tokens
        self._cleanup_expired()

    def _remove_token(self, token: str):
        """Remove a token from blacklist and user tracking."""
        if token in self._blacklist:
            del self._blacklist[token]

        # Remove from user tracking
        for user_id, tokens in self._user_tokens.items():
            if token in tokens:
                tokens.discard(token)
                if not tokens:  # Remove empty sets
                    del self._user_tokens[user_id]
                break

    def _cleanup_expired(self):
        """Remove expired tokens from blacklist to prevent memory bloat."""
        current_time = time.time()
        expired_tokens = [token for token, exp_time in self._blacklist.items() if current_time > exp_time]
        for token in expired_tokens:
            self._remove_token(token)

    def clear(self):
        """Clear all tokens from blacklist. Used for testing."""
        self._blacklist.clear()
        self._user_tokens.clear()

# Global blacklist instance
token_blacklist = TokenBlacklist()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # Add a unique identifier to ensure tokens are unique even with same payload
    to_encode.update({"jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Debug logging
    print(f"DEBUG: Verifying token: {token[:20]}...")
    print(f"DEBUG: Token blacklisted: {token_blacklist.is_blacklisted(token)}")
    print(f"DEBUG: Blacklist size: {len(token_blacklist._blacklist)}")
    print(f"DEBUG: Blacklist ID: {id(token_blacklist)}")

    # Check if token is blacklisted
    if token_blacklist.is_blacklisted(token):
        print(f"DEBUG: Token is blacklisted, raising exception")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception
        
        # Check if subject is a user ID (new format) or email (legacy format)
        if subject.isdigit():
            # New format: subject is user_id
            user_id = int(subject)
            email = payload.get("email")  # email is optional in new format
            token_data = TokenData(email=email, user_id=user_id)
            print(f"DEBUG: Token verification successful for user ID: {user_id}")
        else:
            # Legacy format: subject is email
            email = subject
            user_id = payload.get("user_id")  # user_id might be available
            token_data = TokenData(email=email, user_id=user_id)
            print(f"DEBUG: Token verification successful for email: {email}")
        
        return token_data
    except JWTError:
        print(f"DEBUG: JWT decode failed")
        raise credentials_exception

def revoke_token(token: str):
    """Add a token to the blacklist."""
    try:
        # Decode token to get expiration time and user ID
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        user_id = payload.get("user_id")
        if exp_timestamp:
            token_blacklist.add_token(token, exp_timestamp, user_id)
    except JWTError:
        # If token is invalid, no need to blacklist it
        pass

def revoke_all_user_tokens(user_id: int):
    """Revoke all tokens belonging to a specific user."""
    print(f"DEBUG: Revoking all tokens for user {user_id}")
    print(f"DEBUG: Blacklist ID in revoke: {id(token_blacklist)}")
    print(f"DEBUG: User tokens before revoke: {len(token_blacklist._user_tokens.get(user_id, set()))}")

    result = token_blacklist.revoke_all_user_tokens(user_id)

    print(f"DEBUG: Blacklist size after revoke: {len(token_blacklist._blacklist)}")
    print(f"DEBUG: User tokens after revoke: {len(token_blacklist._user_tokens.get(user_id, set()))}")

    return result

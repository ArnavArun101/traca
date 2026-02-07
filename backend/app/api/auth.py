from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from passlib.context import CryptContext

from app.db.session import get_session
from app.models.db_models import User
from app.models.schemas import RegisterRequest, LoginRequest, AuthResponse, AuthUser
from app.core.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    if payload.confirm_password and payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    existing = session.exec(
        select(User).where(User.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    user = User(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        hashed_password=_hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(user.id, user.email)
    return AuthResponse(
        status="success",
        message="Registered successfully.",
        user=AuthUser(id=user.id, name=user.name, email=user.email),
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.email == payload.email)
    ).first()
    if not user or not _verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id, user.email)
    return AuthResponse(
        status="success",
        message="Logged in successfully.",
        user=AuthUser(id=user.id, name=user.name, email=user.email),
        token=token,
    )


@router.get("/me", response_model=AuthResponse)
def me(current_user: User = Depends(get_current_user)):
    return AuthResponse(
        status="success",
        message="Authenticated.",
        user=AuthUser(id=current_user.id, name=current_user.name, email=current_user.email),
        token=None,
    )

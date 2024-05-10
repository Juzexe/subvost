from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from app.core.dependecies import AsyncSession, get_session
from app.core.security import create_access_token
from app.schemas import PaymentInfo, Token
from app.services import authenticate_user, create_new_user, get_payment_url

router = APIRouter()

templates = Jinja2Templates(directory="html")


@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(user.id)


@router.post("/register_user", response_model=Token)
async def register_user(
    form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)
) -> Token:
    user = await create_new_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist",
        )
    return create_access_token(user.id)


@router.get("/payment", response_model=PaymentInfo)
async def payment_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="pay.html")


@router.post("/payment", response_model=PaymentInfo)
async def payment(
    email: str = Body(),
    username: str = Body(),
    amount: float = Body(),
    description: str = Body(),
    session: AsyncSession = Depends(get_session),
) -> PaymentInfo:
    payment_url = await get_payment_url(session, email, username, amount, description)
    return PaymentInfo(pay_url=payment_url)

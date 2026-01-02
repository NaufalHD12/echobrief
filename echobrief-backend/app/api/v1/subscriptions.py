import json
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_user
from ...core.config import settings
from ...core.database import get_session
from ...models.subscriptions import SubscriptionStatus
from ...models.users import User
from ...schemas.common import ApiResponse
from ...schemas.subscriptions import UserSubscriptionResponse
from ...schemas.users import UserUpdate
from ...services.subscription_service import SubscriptionService
from ...services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


async def get_subscription_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SubscriptionService:
    return SubscriptionService(session)


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)


def verify_kofi_token(verification_token: str) -> bool:
    """Verify webhook verification token from Ko-fi"""
    return verification_token == settings.KOFI_VERIFICATION_TOKEN


@router.post("/webhooks/kofi", response_model=ApiResponse[dict])
async def kofi_webhook(
    request: Request,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Handle webhooks from Ko-fi for payment events.

    Ko-fi sends application/x-www-form-urlencoded with 'data' field containing JSON string.
    Expected types: Donation, Subscription, Commission, Shop Order
    """
    try:
        # Ko-fi sends application/x-www-form-urlencoded
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        
        # Parse form-urlencoded data
        from urllib.parse import parse_qs
        parsed = parse_qs(body_str)
        
        if 'data' not in parsed:
            raise HTTPException(status_code=400, detail="Missing data field")
        
        data_str = parsed['data'][0]
        if not data_str:
            raise HTTPException(status_code=400, detail="Empty data field")
        
        # Parse JSON data from the 'data' field
        data = json.loads(data_str)
        
        # Verify verification token
        verification_token = data.get("verification_token")
        if not verification_token:
            raise HTTPException(status_code=400, detail="Missing verification token")
        
        if not verify_kofi_token(verification_token):
            raise HTTPException(status_code=401, detail="Invalid verification token")
        
        event_type = data.get("type")
        message_id = data.get("message_id")
        
        logger.info(f"Received Ko-fi webhook: type={event_type}, message_id={message_id}")
        
        # Handle based on event type
        if event_type == "Subscription":
            await handle_kofi_subscription(data, subscription_service, user_service)
        elif event_type == "Donation":
            logger.info(f"Donation received: {data.get('from_name')} - {data.get('amount')}")
        elif event_type == "Commission":
            logger.info(f"Commission received: {data.get('from_name')}")
        elif event_type == "Shop Order":
            logger.info(f"Shop order received: {data.get('from_name')}")
        else:
            logger.warning(f"Unknown event type: {event_type}")
        
        return ApiResponse(
            message="Webhook processed successfully", 
            data={"event_type": event_type, "message_id": message_id}
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in data field")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_kofi_subscription(
    data: dict, subscription_service: SubscriptionService, user_service: UserService
) -> None:
    """Handle Ko-fi subscription events"""
    email = data.get("email")
    kofi_transaction_id = data.get("kofi_transaction_id")
    is_subscription_payment = data.get("is_subscription_payment", False)
    is_first_subscription_payment = data.get("is_first_subscription_payment", False)
    tier_name = data.get("tier_name")
    amount = data.get("amount")
    
    if not email:
        logger.warning(f"Missing email in subscription data: {data}")
        return
    
    # Find user by email
    user = await user_service.get_user_by_email(email)
    if not user:
        logger.warning(f"User not found for email: {email}")
        return
    
    logger.info(f"Processing subscription for user {user.id}, email: {email}")
    logger.info(f"Transaction: {kofi_transaction_id}, First: {is_first_subscription_payment}, Recurring: {is_subscription_payment}")
    
    try:
        if is_first_subscription_payment:
            # New subscription
            if not kofi_transaction_id:
                logger.error(f"Missing kofi_transaction_id for new subscription: {data}")
                return
            
            # Check if subscription already exists
            existing = await subscription_service.get_subscription_by_kofi_transaction_id(kofi_transaction_id)
            if existing:
                logger.info(f"Subscription already exists for transaction {kofi_transaction_id}")
                return
            
            # Create new subscription
            subscription = await subscription_service.create_kofi_subscription(
                user_id=user.id,
                kofi_transaction_id=kofi_transaction_id,
                tier_name=tier_name,
                amount=amount
            )
            
            # Update user plan to paid
            user_update = UserUpdate(plan_type="paid")
            await user_service.update_user(
                user.id, user_update, None  # No current user context for admin operation
            )
            
            logger.info(f"Created new subscription {subscription.id} for user {user.id}")
            
        elif is_subscription_payment:
            # Recurring payment for existing subscription
            if not kofi_transaction_id:
                logger.error(f"Missing kofi_transaction_id for recurring payment: {data}")
                return
            
            # Find subscription by transaction ID
            subscription = await subscription_service.get_subscription_by_kofi_transaction_id(kofi_transaction_id)
            if subscription:
                # Update subscription status to active if it was cancelled
                if subscription.status != SubscriptionStatus.active:
                    subscription.status = SubscriptionStatus.active
                    subscription.updated_at = datetime.now(timezone.utc)
                    await subscription_service.session.commit()
                    logger.info(f"Reactivated subscription {subscription.id} for recurring payment")
                else:
                    logger.info(f"Subscription {subscription.id} already active for recurring payment")
            else:
                logger.warning(f"No subscription found for transaction {kofi_transaction_id}, creating new one")
                # Create new subscription for recurring payment without first payment flag
                subscription = await subscription_service.create_kofi_subscription(
                    user_id=user.id,
                    kofi_transaction_id=kofi_transaction_id,
                    tier_name=tier_name,
                    amount=amount
                )
                logger.info(f"Created subscription {subscription.id} for recurring payment")
        
        else:
            # Subscription cancellation or other event
            # Ko-fi doesn't send explicit cancellation events, we need to handle via grace period
            logger.info(f"Non-payment subscription event: {data.get('type')}")
            
    except Exception as e:
        logger.error(f"Error handling Ko-fi subscription: {e}", exc_info=True)


@router.get("/me", response_model=ApiResponse[UserSubscriptionResponse | None])
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> ApiResponse[UserSubscriptionResponse | None]:
    """
    Get current user's active subscription.

    Returns the active subscription if user has one, otherwise returns None.
    """
    subscription = await subscription_service.get_user_subscription(current_user.id)

    if subscription:
        return ApiResponse(
            message="Subscription retrieved successfully",
            data=UserSubscriptionResponse.model_validate(subscription),
        )
    else:
        return ApiResponse(message="No active subscription found", data=None)


@router.get("/plan-type", response_model=ApiResponse[dict])
async def get_user_plan_type(
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> ApiResponse[dict]:
    """
    Get current user's effective plan type.

    Returns the effective plan type considering active subscriptions.
    """
    plan_type = await subscription_service.get_user_plan_type(current_user.id)

    return ApiResponse(
        message="Plan type retrieved successfully",
        data={"plan_type": plan_type, "is_premium": plan_type == "paid"},
    )

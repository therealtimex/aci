import time
from datetime import datetime
from typing import Annotated
from uuid import UUID

import stripe
from fastapi import APIRouter, Body, Depends, Header, Request, status
from propelauth_fastapi import User
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aci.common.db import crud
from aci.common.db.sql_models import Subscription
from aci.common.enums import (
    OrganizationRole,
    StripeSubscriptionInterval,
    StripeSubscriptionStatus,
)
from aci.common.exceptions import BillingError, SubscriptionPlanNotFound
from aci.common.logging_setup import get_logger
from aci.common.schemas.plans import PlanFeatures
from aci.common.schemas.quota import PlanInfo, QuotaUsageResponse
from aci.common.schemas.subscription import (
    StripeCheckoutSessionCreate,
    StripeSubscriptionDetails,
    StripeSubscriptionMetadata,
    SubscriptionPublic,
    SubscriptionUpdate,
)
from aci.server import acl, billing, config
from aci.server import dependencies as deps

router = APIRouter()
logger = get_logger(__name__)

auth = acl.get_propelauth()


@router.get("/get-subscription", response_model=SubscriptionPublic)
async def get_subscription(
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    org_id: Annotated[UUID, Header(alias=config.ACI_ORG_ID_HEADER)],
    user: Annotated[User, Depends(auth.require_user)],
) -> SubscriptionPublic:
    acl.require_org_member(user, org_id)

    active_subscription = crud.subscriptions.get_subscription_by_org_id(db_session, org_id)
    if not active_subscription:
        logger.info(
            "no active subscription found, the org is on the free plan",
            extra={"org_id": org_id},
        )
        return SubscriptionPublic(
            plan="free",
            status=StripeSubscriptionStatus.ACTIVE,
        )

    plan = crud.plans.get_by_id(db_session, active_subscription.plan_id)
    if not plan:
        logger.error(
            "plan not found",
            extra={"plan_id": active_subscription.plan_id},
        )
        raise SubscriptionPlanNotFound(f"plan={active_subscription.plan_id} not found")
    return SubscriptionPublic(
        plan=plan.name,
        status=active_subscription.status,
    )


@router.get("/quota-usage", response_model=QuotaUsageResponse)
async def get_quota_usage(
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    org_id: Annotated[UUID, Header(alias="X-ACI-ORG-ID")],
    user: Annotated[User, Depends(auth.require_user)],
) -> QuotaUsageResponse:
    acl.require_org_member(user, org_id)

    active_plan = billing.get_active_plan_by_org_id(db_session, org_id)
    logger.info(f"Getting quota usage, org_id={org_id}, plan={active_plan.name}")

    projects_used = len(crud.projects.get_projects_by_org(db_session, org_id))
    agent_credentials_used = crud.secret.get_total_number_of_agent_secrets_for_org(
        db_session, org_id
    )
    linked_accounts_used = crud.linked_accounts.get_total_number_of_unique_linked_account_owner_ids(
        db_session, org_id
    )
    total_monthly_api_calls_used_of_org = crud.projects.get_total_monthly_quota_usage_for_org(
        db_session, org_id
    )

    return QuotaUsageResponse(
        projects_used=projects_used,
        linked_accounts_used=linked_accounts_used,
        agent_credentials_used=agent_credentials_used,
        api_calls_used=total_monthly_api_calls_used_of_org,
        plan=PlanInfo(name=active_plan.name, features=PlanFeatures(**active_plan.features)),
    )


@router.post("/create-checkout-session")
async def create_checkout_session(
    user: Annotated[User, Depends(auth.require_user)],
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    org_id: Annotated[UUID, Header(alias=config.ACI_ORG_ID_HEADER)],
    body: Annotated[StripeCheckoutSessionCreate, Body()],
) -> str:
    acl.require_org_member_with_minimum_role(user, org_id, OrganizationRole.ADMIN)

    plan = crud.plans.get_by_name(db_session, body.plan_name)
    if not plan:
        logger.error(f"Plan not found, plan_name={body.plan_name}")
        raise SubscriptionPlanNotFound(f"Plan={body.plan_name} not found")

    price_id = (
        plan.stripe_monthly_price_id
        if body.interval == StripeSubscriptionInterval.MONTH
        else plan.stripe_yearly_price_id
    )

    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=f"{config.DEV_PORTAL_URL}/settings",
            cancel_url=f"{config.DEV_PORTAL_URL}/pricing",
            mode="subscription",
            client_reference_id=str(org_id),
            ui_mode="hosted",
            billing_address_collection="required",
            customer_email=user.email,
            metadata=StripeSubscriptionMetadata(
                org_id=org_id,
                checkout_user_id=user.user_id,
                checkout_user_email=user.email,
            ).model_dump(),
        )
    except stripe.StripeError as e:
        logger.error(f"Error creating checkout session, error={e}")
        raise BillingError() from e

    if not session.url:
        logger.error(f"Checkout session url not found, session={session}")
        raise BillingError("Checkout session url not found")

    return session.url


@router.post("/create-customer-portal-session")
async def create_customer_portal_session(
    user: Annotated[User, Depends(auth.require_user)],
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    org_id: Annotated[UUID, Header(alias=config.ACI_ORG_ID_HEADER)],
) -> str:
    acl.require_org_member_with_minimum_role(user, org_id, OrganizationRole.ADMIN)

    active_subscription = crud.subscriptions.get_subscription_by_org_id(db_session, org_id)
    if not active_subscription:
        logger.error(f"Subscription not found, the org is on the free plan, org_id={org_id}")
        raise BillingError(
            "Subscription not found, the org is on the free plan",
            error_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=active_subscription.stripe_customer_id,
            return_url=f"{config.DEV_PORTAL_URL}/settings",
        )
    except stripe.StripeError as e:
        logger.error(f"Error creating customer portal session, error={e}")
        raise BillingError() from e

    return session.url


@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    stripe_signature: str = Header(None),
) -> None:
    payload = await request.body()
    event = None

    # 1. Verify Signature
    try:
        event = stripe.Webhook.construct_event(  # type: ignore
            payload, stripe_signature, config.STRIPE_WEBHOOK_SIGNING_SECRET
        )
        logger.info(f"Received valid Stripe event, event_id={event.id}, event_type={event.type}")
    except stripe.InvalidRequestError as e:
        logger.error(f"Webhook error: Invalid payload error={e}")
        raise BillingError(
            error_code=status.HTTP_400_BAD_REQUEST,
        ) from e
    except stripe.SignatureVerificationError as e:
        logger.error(f"Webhook error: Invalid signature error={e}")
        raise BillingError(
            error_code=status.HTTP_400_BAD_REQUEST,
        ) from e
    except stripe.StripeError as e:
        logger.error(f"Webhook error: Unexpected error during event construction error={e}")
        raise BillingError() from e

    # 2. Idempotency Check: if event has already been processed, return directly
    # Don't need to worry about race condition or locking here because our event
    # handlers are idempotent. The worst case is just the event is processed twice,
    # but only one of the two inserted into the processed_stripe_event table.
    if crud.processed_stripe_event.is_event_processed(db_session, event.id):
        logger.info(f"Event already processed, skipping, event_id={event.id}")
        return

    # 3. Handle the event
    start_time = time.time()
    logger.info(f"Processing event, event_id={event.id}, event_type={event.type}")

    match event.type:
        case "checkout.session.completed":
            await handle_checkout_session_completed(event.data.object, db_session)
        case "customer.subscription.updated":
            await handle_customer_subscription_updated(event.data.object, db_session)
        case "customer.subscription.deleted":
            await handle_customer_subscription_deleted(event.data.object, db_session)
        case _:
            logger.warning(f"Unhandled event, event_id={event.id}, event_type={event.type}")
            return

    # 4. Record Processed Event
    try:
        crud.processed_stripe_event.record_processed_event(db_session, event.id)
        db_session.commit()
    except IntegrityError as e:
        logger.warning(
            f"The event has already been processed and inserted into the processed_stripe_event table, "
            f"event_id={event.id}, error={e}"
        )
        return

    processing_time = time.time() - start_time
    logger.info(
        f"Successfully processed and recorded event, event_id={event.id}, event_type={event.type}, "
        f"processing_time={processing_time}"
    )


async def handle_checkout_session_completed(session_data: dict, db_session: Session) -> None:
    """
    Handles the checkout.session.completed event.
    1. Retrieve the client_reference_id and subscription details from the session data
    2. Retrieve the subscription details from Stripe
    3. Find the plan corresponding to the subscription price id
    4. Check if a subscription record already exists for this org. If it does, check
    the stripe_subscription_id to make sure it matches. If it doesn't match, log an
    error and return an error code. If it does match, no-op.
    5. Create the new Subscription record
    """
    logger.info(f"Handling checkout.session.completed event, session_data={session_data}")
    # TODO: find out how to use the construct_from method
    # session = stripe.checkout.Session.construct_from(session_data, None)

    # 1. Retrieve the client_reference_id and subscription details from the session data
    client_reference_id = session_data.get("client_reference_id")
    stripe_customer_id = session_data.get("customer")
    stripe_subscription_id = session_data.get("subscription")

    if not client_reference_id or not stripe_customer_id or not stripe_subscription_id:
        logger.error(
            f"Missing critical data in checkout.session.completed event payload, "
            f"session_data={session_data}"
        )
        raise BillingError(
            "Missing critical data in checkout.session.completed event payload.",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    # 2. Retrieve the subscription details from Stripe
    try:
        stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        logger.info(f"Retrieved subscription, stripe_subscription_id={stripe_subscription_id}")
    except stripe.StripeError as e:
        logger.error(
            f"Failed to retrieve subscription, stripe_subscription_id={stripe_subscription_id}, error={e}"
        )
        raise BillingError() from e

    subscription_details = _parse_stripe_subscription_details(stripe_subscription)

    # 3. Find the plan corresponding to the subscription price id
    plan = crud.plans.get_by_stripe_price_id(db_session, subscription_details.stripe_price_id)
    if not plan:
        logger.error(
            f"Could not find internal plan matching stripe price id, stripe_price_id={subscription_details.stripe_price_id}"
        )
        raise BillingError(
            f"Could not find internal plan matching stripe price id, stripe_price_id={subscription_details.stripe_price_id}",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    # 4. Check if a subscription record already exists for this org. If it does, check
    # the stripe_subscription_id to make sure it matches. If it doesn't match, log an
    # error and return an error code. If it does match, no-op.
    existing_sub = crud.subscriptions.get_subscription_by_stripe_id(
        db_session, subscription_details.stripe_subscription_id
    )
    if existing_sub:
        logger.info(
            f"Subscription record already exists, updating org_id={client_reference_id}, stripe_subscription_id={stripe_subscription_id}"
        )

        if existing_sub.stripe_subscription_id == subscription_details.stripe_subscription_id:
            # We don't check if the fields are the same because the subscription may
            # have already been updated after creation. This handler only needs to
            # ensure the subscription record is created.
            logger.info(
                f"Subscription record already created for this org, no-op org_id={client_reference_id}, stripe_subscription_id={stripe_subscription_id}"
            )
            return
        else:
            logger.error(
                f"Subscription record already exists for this org, but stripe_subscription_id does not match, "
                f"org_id={client_reference_id}, existing_stripe_subscription_id={existing_sub.stripe_subscription_id}, "
                f"new_stripe_subscription_id={stripe_subscription_id}"
            )
            raise BillingError(
                "Subscription record already exists for this org, but stripe_subscription_id does not match",
                error_code=status.HTTP_400_BAD_REQUEST,
            )
    else:  # 5. Create the new Subscription record
        logger.info(
            f"Creating new subscription record, org_id={client_reference_id}, "
            f"stripe_subscription_id={stripe_subscription_id}"
        )
        new_subscription = Subscription(
            org_id=client_reference_id,
            plan_id=plan.id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            status=StripeSubscriptionStatus(subscription_details.status),
            interval=subscription_details.interval,
            current_period_end=subscription_details.current_period_end,
            cancel_at_period_end=subscription_details.cancel_at_period_end,
        )
        db_session.add(new_subscription)

    # 6. Update PropelAuth organization max_users based on the new plan
    new_max_users = plan.features["developer_seats"]
    try:
        auth.update_org_metadata(org_id=str(client_reference_id), max_users=new_max_users)
        logger.info(
            f"Updated PropelAuth org max_users for new subscription, org_id={client_reference_id}, "
            f"new_max_users={new_max_users}, plan={plan.name}"
        )
    except Exception:
        logger.exception(
            f"Failed to update PropelAuth org max_users for new subscription, "
            f"org_id={client_reference_id}, new_max_users={new_max_users}, plan={plan.name}",
        )
        # Don't fail the webhook if PropelAuth update fails, just log the error
        # The subscription creation in our DB is still valid

    db_session.commit()
    logger.info(
        f"Successfully created/updated subscription record, org_id={client_reference_id}, stripe_subscription_id={stripe_subscription_id}"
    )

    # 7. Update subscription metadata with org_id
    metadata = session_data.get("metadata")
    try:
        subscription_metadata = StripeSubscriptionMetadata.model_validate(metadata)
    except ValidationError as e:
        logger.error(
            f"Invalid metadata in checkout.session.completed event, metadata={metadata}, error={e}"
        )
        return

    stripe.Subscription.modify(
        stripe_subscription_id,
        metadata=subscription_metadata.model_dump(),
    )


async def handle_customer_subscription_updated(
    subscription_data: dict, db_session: Session
) -> None:
    """
    Handles the customer.subscription.updated event.
    1. Find the existing subscription record in db and also retrieve the latest
    subscription object from Stripe using the stripe_subscription_id.
    2. If the subscription record does not exist, there are two possible cases:
        a. Out of order delivery: the subscription was immediately updated after
        user creates the subscription, and the checkout.session.completed event
        has not been handled yet.
        b. Out of order event: the subscription was updated and then immediately
        deleted. The customer.subscription.deleted was handled before this event.
       If the subscription status of the latest subscription object from Stripe
       is not canceled, then it's case a, otherwise it's case b.
       For case a, we return an error code to trigger a retry.
       For case b, we return 200.
    3. If the subscription record exists, we update the subscription record with
    the details from the latest subscription object from Stripe.
    """
    logger.info(
        f"Handling customer.subscription.updated event, subscription_data={subscription_data}"
    )

    stripe_subscription_id = subscription_data.get("id")
    if not stripe_subscription_id:
        logger.error(f"Subscription updated event missing ID, payload={subscription_data}")
        raise BillingError(
            "Subscription updated event missing ID",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    # 1.1 Find the existing subscription record in db using the stripe_subscription_id.
    subscription = crud.subscriptions.get_subscription_by_stripe_id(
        db_session, stripe_subscription_id
    )
    # 1.2 Retrieve the latest subscription object from Stripe using the stripe_subscription_id.
    try:
        latest_subscription_data = stripe.Subscription.retrieve(stripe_subscription_id)
        latest_subscription_details = _parse_stripe_subscription_details(latest_subscription_data)
        logger.info(
            f"Retrieved latest subscription details from Stripe, latest_subscription_details={latest_subscription_details}"
        )
    except stripe.StripeError as e:
        logger.error(
            f"Failed to retrieve subscription, stripe_subscription_id={stripe_subscription_id}, error={e}"
        )
        raise BillingError() from e

    if not subscription:
        # 2. Handle out of order delivery
        logger.error(
            f"Could not find existing Subscription record to update, "
            f"stripe_subscription_id={latest_subscription_details.stripe_subscription_id}"
        )
        if latest_subscription_details.status != StripeSubscriptionStatus.CANCELED:
            # case a: subscription has yet to be created, need to retry
            raise BillingError(
                f"Could not find existing subscription record to update, "
                f"stripe_subscription_id={latest_subscription_details.stripe_subscription_id}",
                error_code=status.HTTP_404_NOT_FOUND,
            )
        else:
            # case b: subscription has already been deleted, don't need to retry
            logger.info(
                f"Subscription has already been deleted, no-op stripe_subscription_id={latest_subscription_details.stripe_subscription_id}"
            )
            return

    # 3. If the subscription record exists, we update the subscription record with
    # the details from the latest subscription object from Stripe.
    plan = crud.plans.get_by_stripe_price_id(
        db_session, latest_subscription_details.stripe_price_id
    )
    if not plan:
        logger.error(
            f"Could not find internal plan matching stripe price id, "
            f"stripe_price_id={latest_subscription_details.stripe_price_id}"
        )
        raise BillingError(
            f"Could not find internal plan matching stripe price id, "
            f"stripe_price_id={latest_subscription_details.stripe_price_id}",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    # 4. Update the subscription record with the new details
    update_data = SubscriptionUpdate(
        status=StripeSubscriptionStatus(latest_subscription_details.status),
        plan_id=plan.id,
        interval=latest_subscription_details.interval,
        current_period_end=latest_subscription_details.current_period_end,
        cancel_at_period_end=latest_subscription_details.cancel_at_period_end,
        stripe_customer_id=latest_subscription_details.stripe_customer_id,
    )

    subscription = crud.subscriptions.update_subscription_by_stripe_id(
        db_session,
        latest_subscription_details.stripe_subscription_id,
        update_data,
    )
    if not subscription:
        logger.error(
            f"Could not find existing Subscription record to update "
            f"stripe_subscription_id={latest_subscription_details.stripe_subscription_id}"
        )
        raise BillingError(
            "Could not find existing Subscription record to update",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    # 5. Update PropelAuth organization max_users based on the new plan
    new_max_users = plan.features["developer_seats"]
    try:
        auth.update_org_metadata(org_id=str(subscription.org_id), max_users=new_max_users)
        logger.info(
            f"Updated PropelAuth org max_users, org_id={subscription.org_id}, "
            f"new_max_users={new_max_users}, plan={plan.name}"
        )
    except Exception:
        logger.exception(
            f"Failed to update PropelAuth org max_users, org_id={subscription.org_id}, "
            f"new_max_users={new_max_users}, plan={plan.name}",
        )
        # Don't fail the webhook if PropelAuth update fails, just log the error
        # The subscription update in our DB is still valid

    db_session.commit()

    logger.info(
        f"Successfully updated subscription record, stripe_subscription_id={latest_subscription_details.stripe_subscription_id}"
    )


async def handle_customer_subscription_deleted(
    subscription_data: dict, db_session: Session
) -> None:
    """
    Handles the customer.subscription.deleted event.
    1. Find the existing subscription record by stripe_subscription_id
    2. Delete the subscription record
    """
    logger.info(
        f"Handling customer.subscription.deleted event, subscription_data={subscription_data}"
    )
    stripe_subscription_id = subscription_data.get("id")

    if not stripe_subscription_id:
        logger.error(f"Subscription deleted event missing ID, payload={subscription_data}")
        raise BillingError(
            "Subscription deleted event missing ID",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    # 1. Find the existing subscription record by stripe_subscription_id
    subscription = crud.subscriptions.get_subscription_by_stripe_id(
        db_session, stripe_subscription_id
    )

    if subscription:
        # 2. Update PropelAuth organization max_users to free plan limit
        try:
            # Get the free plan to determine the correct max_users value
            plan = crud.plans.get_by_name(db_session, "free")
            if not plan:
                logger.exception(f"Free plan not found, org_id={subscription.org_id}")
                raise BillingError(
                    "Free plan not found",
                    error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            max_users = plan.features["developer_seats"]
            logger.info(
                f"Using developer_seats from free plan, plan={plan.name}, max_users={max_users}"
            )

            # TODO: Update when allowing multiple orgs
            auth.update_org_metadata(org_id=str(subscription.org_id), max_users=max_users)
            logger.info(
                f"Updated PropelAuth org max_users to free plan limit for deleted subscription, "
                f"org_id={subscription.org_id}, max_users={max_users}"
            )
        except Exception:
            logger.exception(
                f"Failed to update PropelAuth org max_users for deleted subscription, "
                f"org_id={subscription.org_id}",
            )
            # Don't fail the webhook if PropelAuth update fails, just log the error

        # 3. Delete the subscription record
        logger.info(
            f"Deleting subscription record, stripe_subscription_id={stripe_subscription_id}, "
            f"org_id={subscription.org_id}, plan_id={subscription.plan_id}"
        )
        crud.subscriptions.delete_subscription_by_stripe_id(db_session, stripe_subscription_id)
        db_session.commit()
    else:
        logger.error(
            f"Subscription record not found, stripe_subscription_id={stripe_subscription_id}"
        )
        raise BillingError(
            "Subscription record not found",
            error_code=status.HTTP_404_NOT_FOUND,
        )


def _parse_stripe_subscription_details(
    subscription_data: dict,
) -> StripeSubscriptionDetails:
    """
    Parse the Stripe subscription details from a Stripe subscription dict based on the
    schema: https://docs.stripe.com/api/subscriptions/retrieve?lang=python
    """
    logger.info(f"Parsing Stripe subscription details, subscription_data={subscription_data}")
    stripe_subscription_id = subscription_data.get("id")
    stripe_customer_id = subscription_data.get("customer")
    status = subscription_data.get("status")
    cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)
    current_period_end_ts = subscription_data.get("current_period_end", 0)
    current_period_end_dt = datetime.fromtimestamp(current_period_end_ts)

    items_data = subscription_data.get("items", {}).get("data", [])
    price = items_data[0].get("price", {})
    interval = price.get("recurring", {}).get("interval")
    stripe_price_id = price.get("id")
    subscription_interval = (
        StripeSubscriptionInterval.MONTH if interval == "month" else StripeSubscriptionInterval.YEAR
    )

    return StripeSubscriptionDetails(
        stripe_subscription_id=stripe_subscription_id,  # type: ignore
        stripe_customer_id=stripe_customer_id,  # type: ignore
        status=StripeSubscriptionStatus(status),  # type: ignore
        current_period_end=current_period_end_dt,
        cancel_at_period_end=cancel_at_period_end,
        stripe_price_id=stripe_price_id,
        interval=subscription_interval,
    )

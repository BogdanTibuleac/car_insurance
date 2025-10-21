from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import localdate, now
from django.db import transaction
#import logging
import structlog

from apps.policies.models import InsurancePolicy, InsuranceExpiryLog

#logger = logging.getLogger(__name__)
logger = structlog.get_logger()

def log_policy_expirations():
    """
    Logs expiration of insurance policies that have ended before today
    and have not yet been logged.
    """
    today = localdate()
    logger.info(f"Starting insurance policy expiration logging task.")
    with transaction.atomic():
        already_logged_ids = InsuranceExpiryLog.objects.values_list('policy_id', flat=True)
        expiring_policies = (
            InsurancePolicy.objects
            .select_for_update(skip_locked=True)
            .filter(end_date__lte=today, logged_expiry_at__isnull=True)
            .exclude(id__in=already_logged_ids)  # Ensure no existing log
        )
        for policy in expiring_policies:
            InsuranceExpiryLog.objects.create(policy=policy, logged_at=now())
            logger.info(f"Logged expiration for InsurancePolicy id={policy.id} for car {policy.car.id}.")
    logger.info("Policy expiry job completed.")
    
    
def start_scheduler():
    """
    Starts the background scheduler to run periodic tasks.
    """
    scheduler = BackgroundScheduler(timezone="Europe/Bucharest")
    scheduler.add_job(log_policy_expirations, trigger = 'interval', minutes = 1, next_run_time=now(), id="log_policy_expirations_job", replace_existing=True)
    scheduler.start()
    logger.info("Background scheduler started.")    
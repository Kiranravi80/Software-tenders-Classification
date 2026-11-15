from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

retry_request = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(
        multiplier=1,
        min=2,
        max=30
    ),
    reraise=True
)
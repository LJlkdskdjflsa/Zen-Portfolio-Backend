"""
Time utility module.

This module provides standardized time handling functions for the application.
All time operations should use these utilities to ensure consistency.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Tuple


def get_current_utc() -> datetime:
    """Get current UTC datetime.

    Returns:
        datetime: Current UTC datetime with timezone information
    """
    return datetime.now(timezone.utc)


def get_current_timestamp() -> int:
    """Get current UTC timestamp in seconds.

    Returns:
        int: Current UTC timestamp in seconds
    """
    return int(get_current_utc().timestamp())


def to_utc_datetime(timestamp: Union[int, float]) -> datetime:
    """Convert timestamp to UTC datetime.

    Args:
        timestamp (Union[int, float]): Unix timestamp in seconds

    Returns:
        datetime: UTC datetime with timezone information
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def get_transaction_signature_range(
    last_fetch_signature: Optional[str] = None,
    first_verified_signature: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Get the signature range for transaction fetching.
    From last fetch signature (or first verified signature) to current.

    Args:
        last_fetch_signature (Optional[str]): Last successful fetch signature
        first_verified_signature (Optional[str]): First verification signature of the account,
            used as start signature if last_fetch_signature is None

    Returns:
        Tuple[Optional[str], Optional[str]]: Tuple of (before_signature, until_signature)
                        both will be None if no signatures are provided
    """
    # If last_fetch_signature exists, use that
    if last_fetch_signature is not None:
        return (None, last_fetch_signature)
    
    # If no last_fetch_signature but first_verified_signature exists, use that
    if first_verified_signature is not None:
        return (first_verified_signature, None)
    
    # If neither exists, return None for both
    return (None, None)


def format_datetime_for_db(dt: datetime) -> datetime:
    """Format datetime for database storage.
    Ensures datetime has UTC timezone before storage.

    Args:
        dt (datetime): Datetime to format

    Returns:
        datetime: UTC datetime with timezone information
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_db_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """Parse datetime from database.
    Ensures retrieved datetime has UTC timezone.

    Args:
        dt (Optional[datetime]): Datetime from database

    Returns:
        Optional[datetime]: UTC datetime with timezone information or None
    """
    if dt is None:
        return None
        
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def get_datetime_range(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    hours: Optional[int] = None,
    days: Optional[int] = None
) -> Tuple[datetime, datetime]:
    """Get a datetime range based on various parameters.

    Args:
        start_time (Optional[datetime]): Start time
        end_time (Optional[datetime]): End time
        hours (Optional[int]): Hours to look back from end_time
        days (Optional[int]): Days to look back from end_time

    Returns:
        Tuple[datetime, datetime]: (start_datetime, end_datetime) with timezone
    """
    end = end_time if end_time else get_current_utc()
    
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    
    if start_time:
        start = start_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
    elif hours is not None:
        start = end - timedelta(hours=hours)
    elif days is not None:
        start = end - timedelta(days=days)
    else:
        start = end - timedelta(days=1)  # Default to 1 day
        
    return start, end 
import json
from typing import List, Dict, Any, Union
import logging

from app.utils.transfer_parser import parse_transfers
from app.utils.swap_parser import parse_swaps

# Configure logging
logger = logging.getLogger(__name__)


def process_helius_webhook(data: Union[str, List[Dict[str, Any]]], creator_id: str) -> Dict[str, List]:
    """
    Process Helius webhook data and convert to model objects.
    
    Args:
        data (Union[str, List[Dict[str, Any]]]): JSON string or parsed JSON data from Helius webhook
        creator_id (str): ID of the creator for audit fields
        
    Returns:
        Dict[str, List]: Dictionary with 'transfers' and 'swaps' keys containing lists of model objects
    """
    logger.info("Processing Helius webhook data")
    
    # Parse JSON if string is provided
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}", exc_info=True)
            return {"transfers": [], "swaps": []}
    
    # Parse transfers and swaps using dedicated parsers
    transfers = parse_transfers(data, creator_id=creator_id)
    swaps = parse_swaps(data, creator_id=creator_id)
    
    logger.info(f"Processed webhook data: {len(transfers)} transfers, {len(swaps)} swaps")
    return {
        "transfers": transfers,
        "swaps": swaps
    } 
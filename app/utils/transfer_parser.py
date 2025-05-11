from typing import List, Dict, Any
import logging
from datetime import datetime

from app.models.SolanaTransaction import TokenTransfer, TransactionType

# Configure logging
logger = logging.getLogger(__name__)


def parse_transfer(item: Dict[str, Any], creator_id: str) -> List[TokenTransfer]:
    """
    Parse a single transfer transaction from Helius webhook data.
    
    Args:
        item (Dict[str, Any]): A single transaction item from Helius webhook
        creator_id (str): ID of the creator for audit fields
        
    Returns:
        List[TokenTransfer]: List of TokenTransfer objects from this transaction
    """
    transfers = []
    
    # Skip if not a transfer
    if item.get("type") != "TRANSFER":
        return transfers
        
    # Extract token transfers
    for token_transfer in item.get("tokenTransfers", []):
        try:
            transfer = TokenTransfer(
                signature=item.get("signature"),
                timestamp=item.get("timestamp"),
                slot=item.get("slot"),
                fee=item.get("fee"),
                fee_payer=item.get("feePayer"),
                from_user=token_transfer.get("fromUserAccount"),
                to_user=token_transfer.get("toUserAccount"),
                mint=token_transfer.get("mint"),
                token_amount=token_transfer.get("tokenAmount"),
                decimals=token_transfer.get("rawTokenAmount", {}).get("decimals") if "rawTokenAmount" in token_transfer else None,
                source=item.get("source"),
                transaction_type=TransactionType.TRANSFER,
                gmt_creator=creator_id,
                gmt_created=datetime.now()
            )
            transfers.append(transfer)
            logger.debug(f"Parsed transfer: {item.get('signature')}")
        except Exception as e:
            logger.error(f"Error parsing transfer data: {e}", exc_info=True)
    
    return transfers


def parse_transfers(data: List[Dict[str, Any]], creator_id: str) -> List[TokenTransfer]:
    """
    Parse all token transfers from Helius webhook data.
    
    Args:
        data (List[Dict[str, Any]]): The raw JSON data from Helius webhook
        creator_id (str): ID of the creator for audit fields
        
    Returns:
        List[TokenTransfer]: List of TokenTransfer objects ready to be saved to database
    """
    logger.info(f"Parsing transfer data from Helius webhook with {len(data)} items")
    all_transfers = []
    
    for item in data:
        transfers = parse_transfer(item, creator_id)
        all_transfers.extend(transfers)
    
    logger.info(f"Successfully parsed {len(all_transfers)} transfers")
    return all_transfers 
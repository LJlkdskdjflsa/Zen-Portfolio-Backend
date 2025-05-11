from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from decimal import Decimal

from app.models.SolanaTransaction import TokenSwap, TransactionType

# Configure logging
logger = logging.getLogger(__name__)


def parse_swap(item: Dict[str, Any], creator_id: str) -> Optional[TokenSwap]:
    """
    Parse a single swap transaction from Helius webhook data.
    
    Args:
        item (Dict[str, Any]): A single transaction item from Helius webhook
        creator_id (str): ID of the creator for audit fields
        
    Returns:
        Optional[TokenSwap]: TokenSwap object if successful, None if not a swap or error
    """
    # Skip if not a swap
    if item.get("type") != "SWAP":
        return None
        
    try:
        # Extract swap details from events
        swap_event = item.get("events", {}).get("swap", {})
        
        # Get input (could be native SOL or token)
        input_mint = None
        input_amount = None
        input_decimals = None
        
        # Check for native input (SOL)
        native_input = swap_event.get("nativeInput")
        if native_input:
            input_mint = "So11111111111111111111111111111111111111112"  # SOL mint address
            input_amount = Decimal(native_input.get("amount", "0")) / Decimal(10**9)  # SOL has 9 decimals
            input_decimals = 9
        
        # Check for token inputs (usually just one)
        token_inputs = swap_event.get("tokenInputs", [])
        if token_inputs and len(token_inputs) > 0:
            input_token = token_inputs[0]
            input_mint = input_token.get("mint")
            raw_amount = input_token.get("rawTokenAmount", {})
            input_decimals = raw_amount.get("decimals")
            input_amount = Decimal(raw_amount.get("tokenAmount", "0")) / Decimal(10**input_decimals) if input_decimals else 0
        
        # Get output token
        output_mint = None
        output_amount = None
        output_decimals = None
        
        token_outputs = swap_event.get("tokenOutputs", [])
        if token_outputs and len(token_outputs) > 0:
            output_token = token_outputs[0]
            output_mint = output_token.get("mint")
            raw_amount = output_token.get("rawTokenAmount", {})
            output_decimals = raw_amount.get("decimals")
            output_amount = Decimal(raw_amount.get("tokenAmount", "0")) / Decimal(10**output_decimals) if output_decimals else 0
        
        # Create swap record
        swap = TokenSwap(
            signature=item.get("signature"),
            timestamp=item.get("timestamp"),
            slot=item.get("slot"),
            fee=item.get("fee"),
            fee_payer=item.get("feePayer"),
            user_account=item.get("feePayer"),  # Usually the fee payer is the user doing the swap
            input_mint=input_mint,
            input_amount=input_amount,
            input_decimals=input_decimals,
            output_mint=output_mint,
            output_amount=output_amount,
            output_decimals=output_decimals,
            source=item.get("source"),
            transaction_type=TransactionType.SWAP,
            gmt_creator=creator_id,
            gmt_created=datetime.now()
        )
        logger.debug(f"Parsed swap: {item.get('signature')}")
        return swap
    except Exception as e:
        logger.error(f"Error parsing swap data: {e}", exc_info=True)
        return None


def parse_swaps(data: List[Dict[str, Any]], creator_id: str) -> List[TokenSwap]:
    """
    Parse all token swaps from Helius webhook data.
    
    Args:
        data (List[Dict[str, Any]]): The raw JSON data from Helius webhook
        creator_id (str): ID of the creator for audit fields
        
    Returns:
        List[TokenSwap]: List of TokenSwap objects ready to be saved to database
    """
    logger.info(f"Parsing swap data from Helius webhook with {len(data)} items")
    swaps = []
    
    for item in data:
        swap = parse_swap(item, creator_id)
        if swap:
            swaps.append(swap)
    
    logger.info(f"Successfully parsed {len(swaps)} swaps")
    return swaps 
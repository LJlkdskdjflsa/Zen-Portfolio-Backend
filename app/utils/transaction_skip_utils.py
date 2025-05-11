from app.dtos.historical_transaction_dto import HistoricalTransactionDTO
from app.enums.true_north_transaction_type import TrueNorthTransactionType
from app.enums.helius_enum import TransactionType
from app.utils.logging_util import log_message, LogLevel

def check_if_transaction_needs_skip(tx: HistoricalTransactionDTO, token_address: str) -> bool:
    """
    Check if a transaction needs to be skipped based on missing price information.

    Args:
        tx (HistoricalTransactionDTO): The transaction to check
        token_address (str): The token address to check price for

    Returns:
        bool: True if the transaction needs to be skipped, False otherwise
    """
    
    
    if tx.transaction_type in [TrueNorthTransactionType.TRADE.value, TransactionType.SWAP.value]:
        # For trades/swaps, check if relevant price info exists based on token role
        if (tx.output_token == token_address and tx.output_token and tx.output_token != "" and
            (tx.output_token_price_usd is None or tx.output_token_price_usd <= 0)):
            log_message(
                level=LogLevel.DEBUG,
                event="Skipping buy transaction with missing output price",
                signature=tx.signature,
                token=token_address,
                output_price=tx.output_token_price_usd
            )
            return True
        
        if (tx.input_token == token_address and tx.input_token and tx.input_token != "" and
            (tx.input_token_price_usd is None or tx.input_token_price_usd <= 0)):
            log_message(
                level=LogLevel.DEBUG,
                event="Skipping sell transaction with missing input price",
                signature=tx.signature,
                token=token_address,
                input_price=tx.input_token_price_usd
            )
            return True
        
    elif (tx.transaction_type == TransactionType.TRANSFER.value and
          tx.transfer_token_address == token_address and 
          tx.transfer_token_address and 
          tx.transfer_token_address != "" and
          tx.address_to == tx.user_address and
          (tx.transfer_token_price_usd is None or tx.transfer_token_price_usd <= 0)):
        log_message(
            level=LogLevel.DEBUG,
            event="Skipping deposit transaction with missing transfer price",
            signature=tx.signature,
            token=token_address,
            transfer_price=tx.transfer_token_price_usd
        )
        return True
    
    
    
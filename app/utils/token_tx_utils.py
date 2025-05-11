from app.dtos.historical_transaction_dto import HistoricalTransactionDTO
from typing import List

def filter_token_specific_txs(
    filtered_composed_historical_transaction_dto_list: List[HistoricalTransactionDTO],
    token_address: str,
) -> List[HistoricalTransactionDTO]:
    """
    Filters transactions related to a specific token address.

    Args:
        filtered_composed_historical_transaction_dto_list (List[HistoricalTransactionDTO]): List of transaction DTOs.
        token_address (str): The token address to filter for.

    Returns:
        List[HistoricalTransactionDTO]: Filtered transactions related to the token address.
    """
    return [
        tx
        for tx in filtered_composed_historical_transaction_dto_list
        if (
            (
                tx.input_token == token_address
                and tx.input_token is not None
                and tx.input_token != ""
            )
            or (
                tx.output_token == token_address
                and tx.output_token is not None
                and tx.output_token != ""
            )
            or (
                tx.transfer_token_address == token_address
                and tx.transfer_token_address is not None
                and tx.transfer_token_address != ""
            )
        )
    ]

import requests
from typing import List
from app.dtos.token_dto import TokensResponse


def get_wallet_data_by_solana_tracker(wallet_address: str) -> TokensResponse:
    """
    Fetch token data from the given API URL and validate it using the TokensResponse DTO.
    Returns a TokensResponse object if validation succeeds, otherwise raises ValidationError.
    """
    headers = {
        "User-Agent": "ZenPortfolio/1.0",
    }
    response = requests.get(f"https://data.solanatracker.io/wallet/{wallet_address}", headers=headers)
    response.raise_for_status()  # Raises HTTPError if the request returned an unsuccessful status code
    data = response.json()
    # Validate and parse the data using Pydantic DTO
    tokens_response = TokensResponse.model_validate(data)
    return tokens_response

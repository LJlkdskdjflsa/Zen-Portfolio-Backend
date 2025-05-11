from fastapi import HTTPException, status
import base64
import time
import requests
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    create_idempotent_associated_token_account,
    TOKEN_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
    TOKEN_2022_PROGRAM_ID,
)
from app.utils.logging_util import log_message, LogLevel
from app.infrastructure.settings import settings
import base64
import time
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.keypair import Keypair
from solana.rpc.api import Client


def get_client():
    client = Client(
        f"https://mainnet.helius-rpc.com/?api-key={settings.HELIUS_API_KEY}"
    )
    return client


def create_ata_account_if_not_exists_using_private_key(
    mint_token_address: str, owner_address: str, fee_payer_private_key: str
) -> str:
    """Create Associated Token Account if it doesn't exist using a private key.

    Args:
        mint_token_address: Token mint address
        owner_address: Owner's wallet address
        fee_payer_private_key: Private key in base58 format for the fee payer

    Returns:
        str: ATA address
    """
    # Create keypair from private key
    wallet = Keypair.from_base58_string(fee_payer_private_key)

    mint_token_pubkey = Pubkey.from_string(mint_token_address)
    token_owner = Pubkey.from_string(owner_address)
    client = get_client()
    token_info = client.get_account_info(mint_token_pubkey)

    # Convert addresses to Pubkey objects
    ata_address = get_associated_token_address(
        owner=token_owner, mint=mint_token_pubkey, token_program_id=token_info.value.owner
    )

    log_message(LogLevel.INFO, f"Checking ATA address: {ata_address}")
    client = get_client()
    ata_info = client.get_account_info(ata_address, commitment=Confirmed)

    if ata_info.value is None:
        log_message(LogLevel.INFO, "ATA doesn't exist, creating...")

        instruction = create_idempotent_associated_token_account(
            payer=wallet.pubkey(),
            owner=token_owner,
            mint=mint_token_pubkey,
            token_program_id=token_info.value.owner,
        )

        message = MessageV0.try_compile(
            payer=wallet.pubkey(),
            instructions=[instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=client.get_latest_blockhash().value.blockhash,
        )
        tx = VersionedTransaction(
            message=message,
            keypairs=[wallet],
        )

        # Encode transaction
        encoded_tx = base64.b64encode(bytes(tx)).decode("utf-8")

        # Send transaction
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                encoded_tx,
                {
                    "skipPreflight": True,
                    "preflightCommitment": "finalized",
                    "encoding": "base64",
                    "maxRetries": None,
                    "minContextSlot": None,
                },
            ],

            
        }

        response = requests.post(
            f"https://mainnet.helius-rpc.com/?api-key={settings.HELIUS_API_KEY}",
            headers=headers,
            json=data,
        )

        if response.status_code != 200:
            log_message(LogLevel.ERROR, "Failed to create ATA", error=response.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create ATA: {response.text}",
            )

        result = response.json()
        log_message(LogLevel.INFO, "ATA creation completed", result=result)
        # return str(ata_address)

        # Increase delay and add confirmation check
        max_retries = 5
        for _ in range(max_retries):
            time.sleep(3)  # Increased to 3 seconds
            ata_info = client.get_account_info(ata_address, commitment=Confirmed)
            if ata_info.value is not None:
                log_message(LogLevel.INFO, "ATA creation confirmed")
                time.sleep(15)
                log_message(LogLevel.INFO, "ATA creation confirmed 15 seconds")
                return str(ata_address)

        log_message(LogLevel.ERROR, "ATA creation not confirmed after retries")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="ATA creation not confirmed after multiple retries",
        )
    else:
        log_message(LogLevel.INFO, "ATA already exists")
        return str(ata_address)

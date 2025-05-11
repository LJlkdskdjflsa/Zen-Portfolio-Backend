from decimal import Decimal


APPLICATION_NAME = "execution-agents"
SOLANA_NATIVE_TOKEN_NAME = "SOL"
SOLANA_NATIVE_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"
USDC_TOKEN_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOLANA_NETWORK_ID = 1399811149
FISHING_TRANSACTION_THRESHOLD=0.0001
CREATION_REMOVAL_TRANSACTION_THRESHOLD_MIN = 0.0019
CREATION_REMOVAL_TRANSACTION_THRESHOLD_MAX = 0.0023

# PNL
PNL_CALCULTATION_CLOSE_POSITION_THRESHOLD_USD_VALUE = Decimal('0.0001')  # Threshold for considering a position closed (in USD)

# List of token addresses for which PNL should not be calculated
NOT_SHOW_PNL_TOKEN_LIST = [
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    # Add more stable coin addresses here as needed
]

# codex
CODEX_API_URL = "https://graph.codex.io/graphql"
CODEX_GET_PRICE_API_BATCH_SIZE = 25

# Tolerance for considering SOL transfer amounts the same (e.g., for wrap/unwrap)
SOL_TRANSFER_AMOUNT_TOLERANCE = 0.05

# Cache time 
USER_HOLDINGS_CACHE_SECONDS = 10
TOKEN_PRICE_CACHE_SECONDS = 10
USER_TRANSACTIONS_CACHE_SECONDS = 10

# Gas price
GAS_PRICE_LAMPORTS = 1000_000_000
MAX_PRIORITY_FEE_LAMPORTS = 1_000_000

# Jupiter
JUPITER_BASE_URL = "https://api.jup.ag/swap/v1"

# Helius
HELIUS_BASE_URL="https://mainnet.helius-rpc.com"
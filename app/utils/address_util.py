import re

# EVM addresses: 0x + 40 hex chars (case-insensitive)
EVM_ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")
# Solana addresses: Base58, typically 32 or 44 chars, no 0, O, I, l
BASE58_CHARSET = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")

def is_evm_address(address: str) -> bool:
    return bool(EVM_ADDRESS_REGEX.match(address))

def is_solana_address(address: str) -> bool:
    # Length: usually 32 or 44 chars
    if not (32 <= len(address) <= 44):
        return False
    # All chars in Base58
    return all(c in BASE58_CHARSET for c in address)

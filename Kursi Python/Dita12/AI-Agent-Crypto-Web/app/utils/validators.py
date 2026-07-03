from solders.pubkey import Pubkey


def validate_solana_address(value: str) -> str:
    try:
        Pubkey.from_string(value.strip())
    except ValueError as error:
        raise ValueError("Invalid Solana public address") from error
    return value.strip()

def check_blacklisted_target(ip_address: str, name: str) -> bool:
    target_string = f"{ip_address} {name}".lower()
    blacklisted_extensions = [".gov", ".mil", ".edu.tr", "gov.tr", "mil.tr"]
    for ext in blacklisted_extensions:
        if ext in target_string:
            return True
    return False

def validate_asset_target(target: str) -> bool:
    target_lower = target.lower().strip()
    blacklisted_extensions = [".gov", ".mil", ".edu.tr", "gov.tr", "mil.tr"]
    for ext in blacklisted_extensions:
        if ext in target_lower:
            return False
    return True

from datetime import timezone


def validate_url(v):
    """Reusable URL validator"""
    if not v.startswith(('http://', 'https://')):
        raise ValueError('URL must be HTTP or HTTPS')
    return v


def validate_url_optional(v):
    """Reusable optional URL validator"""
    if v is not None and not v.startswith(('http://', 'https://')):
        raise ValueError('URL must be HTTP or HTTPS')
    return v


def ensure_timezone_aware(v):
    """Reusable datetime timezone validator"""
    if v is not None and v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v


def ensure_timezone_aware_required(v):
    """Reusable required datetime timezone validator"""
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v

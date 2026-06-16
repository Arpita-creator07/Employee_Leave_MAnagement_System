import re
EMAIL_PATTERN = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
NAME_PATTERN = re.compile('^[A-Za-z ]+$')
SPECIAL_CHAR_PATTERN = re.compile('[^A-Za-z0-9]')

def normalize_name(name: str) -> str:
    return ' '.join((name or '').strip().split())

def normalize_email(email: str) -> str:
    return (email or '').strip().lower()

def validate_name(name: str):
    clean_name = normalize_name(name)
    if not clean_name:
        return (False, 'Name is required.', clean_name)
    if clean_name.lower().startswith('no'):
        return (False, "Name cannot start with 'No'.", clean_name)
    if len(clean_name) < 2 or len(clean_name) > 50:
        return (False, 'Name must be between 2 and 50 characters.', clean_name)
    if not NAME_PATTERN.fullmatch(clean_name):
        return (False, 'Name can contain only letters and spaces.', clean_name)
    return (True, '', clean_name)

def validate_email(email: str):
    clean_email = normalize_email(email)
    if not clean_email:
        return (False, 'Email is required.', clean_email)
    if len(clean_email) > 254:
        return (False, 'Email is too long.', clean_email)
    if '..' in clean_email:
        return (False, 'Email format is invalid.', clean_email)
    if not EMAIL_PATTERN.fullmatch(clean_email):
        return (False, 'Enter a valid email address.', clean_email)
    return (True, '', clean_email)

def validate_password(password: str):
    value = (password or '').strip()
    if not value:
        return (False, 'Password is required.')
    if len(value) < 8 or len(value) > 64:
        return (False, 'Password must be 8 to 64 characters long.')
    if any((ch.isspace() for ch in value)):
        return (False, 'Password cannot contain spaces.')
    if not any((ch.islower() for ch in value)):
        return (False, 'Password must include at least one lowercase letter.')
    if not any((ch.isupper() for ch in value)):
        return (False, 'Password must include at least one uppercase letter.')
    if not any((ch.isdigit() for ch in value)):
        return (False, 'Password must include at least one number.')
    if not SPECIAL_CHAR_PATTERN.search(value):
        return (False, 'Password must include at least one special character.')
    return (True, '')

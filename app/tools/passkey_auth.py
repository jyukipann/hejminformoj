from models.about_users import User, Passkey
from webauthn import generate_registration_options, options_to_json
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
)

def to_bytes(data: str) -> bytes:
    return data.encode('utf-8')


def create_user(SessionLocal, username: str, name:str):
    """
    add_passkey() -> bool
    This function is a stub for the add_passkey function.
    """
    with SessionLocal() as session:
        # check if user already exists
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            # add user
            user = User(username=username, name=name)
            session.add(user)
            session.commit()
            user = session.query(User).filter_by(username=username).first()
    # add passkey
    options = generate_registration_options(
        # A name for your "Relying Party" server
        rp_name="juki auth",
        # Your domain on which WebAuthn is being used
        rp_id="hejminformoj.jyukipann.com",
        # An assigned random identifier;
        # never anything user-identifying like an email address
        user_id=to_bytes(user.uuid),
        # A user-visible hint of which account this credential belongs to
        # An email address is fine here
        user_name=user.username,
        # Require the user to verify their identity to the authenticator
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    return options

def to_json(options):
    return options_to_json(options)

def passkey_auth(engine, SessionLocal)->bool:
    """
    passkey_auth() -> bool
    This function is a stub for the passkey authentication function.
    """
    
    return False
import base64

from .. import idol
from .. import util
from ..idol import user
from ..idol import error

import fastapi
import pydantic


class LoginRequest(pydantic.BaseModel):
    login_key: str
    login_passwd: str
    devtoken: str | None = None


class LoginResponse(pydantic.BaseModel):
    authorize_token: str
    user_id: int
    review_version: str = ""
    server_timestamp: int
    idfa_enabled: bool = False
    skip_login_news: bool = False


class AuthkeyRequest(pydantic.BaseModel):
    dummy_token: str
    auth_data: str


class AuthkeyResponse(pydantic.BaseModel):
    authorize_token: str
    dummy_token: str


class StartupResponse(pydantic.BaseModel):
    user_id: str


class LicenseInfo(pydantic.BaseModel):
    license_list: list
    licensed_info: list
    expired_info: list
    badge_flag: bool


class TopInfoResponse(pydantic.BaseModel):
    friend_action_cnt: int
    friend_greet_cnt: int
    friend_variety_cnt: int
    friend_new_cnt: int
    present_cnt: int
    secret_box_badge_flag: int
    server_datetime: str
    server_timestamp: int
    notice_friend_datetime: str
    notice_mail_datetime: str
    friends_approval_wait_cnt: int
    friends_request_cnt: int
    is_today_birthday: bool
    license_info: LicenseInfo
    using_buff_info: list
    is_klab_id_task_flag: bool
    klab_id_task_can_sync: bool
    has_unread_announce: bool
    exchange_badge_cnt: list[int]
    ad_flag: bool
    has_ad_reward: bool


class NotificationStatus(pydantic.BaseModel):
    push: bool
    lp: bool
    update_info: bool
    campaign: bool
    live: bool
    lbonus: bool
    event: bool
    secretbox: bool
    birthday: bool


class TopInfoOnceResponse(pydantic.BaseModel):
    new_achievement_cnt: int
    unaccomplished_achievement_cnt: int
    live_daily_reward_exist: int
    training_energy: int
    training_energy_max: int
    notification: NotificationStatus
    open_arena: bool
    costume_status: bool
    open_accessory: bool
    arena_si_skill_unique_check: bool
    open_v98: bool


@idol.register("/login/login", check_version=False, batchable=False)
def login_login(context: idol.SchoolIdolAuthParams, request: LoginRequest) -> LoginResponse:
    """Login user"""

    # Decrypt credentials
    key = util.xorbytes(context.token.client_key[:16], context.token.server_key[:16])
    loginkey = util.decrypt_aes(key, base64.b64decode(request.login_key))
    passwd = util.decrypt_aes(key, base64.b64decode(request.login_passwd))

    # Log
    util.log("Hello my key is", loginkey)
    util.log("And my passwd is", passwd)

    # Find user
    u = user.find_by_key(context, str(loginkey, "UTF-8"))
    if u is None or (not u.check_passwd(str(passwd, "UTF-8"))):
        # This will send "Your data has been transfered succesfully" message to the SIF client.
        raise error.IdolError(error_code=407, status_code=600, detail="Login not found")

    # Login
    token = util.encapsulate_token(context.token.server_key, context.token.client_key, u.id)
    return LoginResponse(authorize_token=token, user_id=u.id, server_timestamp=util.time())


@idol.register("/login/authkey", check_version=False, batchable=False, xmc_verify=idol.XMCVerifyMode.NONE)
def login_authkey(context: idol.SchoolIdolParams, request: AuthkeyRequest) -> AuthkeyResponse:
    """Generate authentication key."""

    # Decrypt client key
    client_key = util.decrypt_rsa(base64.b64decode(request.dummy_token))
    if not client_key:
        raise fastapi.HTTPException(400, "Bad client key")
    auth_data = util.decrypt_aes(client_key[:16], base64.b64decode(request.auth_data))

    # Create new token
    server_key = util.randbytes(32)
    token = util.encapsulate_token(server_key, client_key, 0)

    # Log
    util.log("My client key is", client_key)
    util.log("And my auth_data is", auth_data)

    # Return response
    return AuthkeyResponse(
        authorize_token=token,
        dummy_token=str(base64.b64encode(server_key), "UTF-8"),
    )


@idol.register("/login/startUp", check_version=False, batchable=False)
def login_startup(context: idol.SchoolIdolAuthParams, request: LoginRequest) -> StartupResponse:
    """Register new account."""
    key = util.xorbytes(context.token.client_key[:16], context.token.server_key[:16])
    loginkey = util.decrypt_aes(key, base64.b64decode(request.login_key))
    passwd = util.decrypt_aes(key, base64.b64decode(request.login_passwd))

    # Log
    util.log("Hello my key is", loginkey)
    util.log("And my passwd is", passwd)

    # Create user
    try:
        u = user.create(context, str(loginkey, "UTF-8"), str(passwd, "UTF-8"))
    except ValueError:
        raise fastapi.HTTPException(400, "Bad login key or password or client key")

    return StartupResponse(user_id=str(u.id))


@idol.register("/login/topInfo")
def login_topinfo(context: idol.SchoolIdolUserParams) -> TopInfoResponse:
    # TODO
    util.log("STUB /login/topInfo", severity=util.logging.WARNING)
    return TopInfoResponse(
        friend_action_cnt=0,
        friend_greet_cnt=0,
        friend_variety_cnt=0,
        friend_new_cnt=0,
        present_cnt=0,
        secret_box_badge_flag=False,
        server_datetime=util.timestamp_to_datetime(),
        server_timestamp=util.time(),
        notice_friend_datetime=util.timestamp_to_datetime(0),
        notice_mail_datetime=util.timestamp_to_datetime(0),
        friends_approval_wait_cnt=0,
        friends_request_cnt=0,
        is_today_birthday=False,
        license_info=LicenseInfo(license_list=[], licensed_info=[], expired_info=[], badge_flag=False),
        using_buff_info=[],
        is_klab_id_task_flag=False,
        klab_id_task_can_sync=False,
        has_unread_announce=False,
        exchange_badge_cnt=[135, 41, 345],
        ad_flag=False,
        has_ad_reward=False,
    )


@idol.register("/login/topInfoOnce")
def login_topinfoonce(context: idol.SchoolIdolUserParams) -> TopInfoOnceResponse:
    # TODO
    util.log("STUB /login/topInfoOnce", severity=util.logging.WARNING)
    return TopInfoOnceResponse(
        new_achievement_cnt=0,
        unaccomplished_achievement_cnt=0,
        live_daily_reward_exist=False,
        training_energy=3,
        training_energy_max=3,
        notification=NotificationStatus(
            push=True,
            lp=False,
            update_info=False,
            campaign=False,
            live=False,
            lbonus=False,
            event=True,
            secretbox=True,
            birthday=True,
        ),
        open_arena=True,
        costume_status=True,
        open_accessory=True,
        arena_si_skill_unique_check=True,
        open_v98=True,
    )

import base64
import hashlib
import hmac
import json
from typing import Literal

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from .. import const
from .. import idoltype
from .. import util
from ..config import config
from ..idol.system import core

SALT_SIZE = 16


class User(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    key: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(index=True)
    passwd: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()

    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(default="Kemp")
    level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    previous_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=core.get_next_exp_cumulative(1))
    game_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    free_sns_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    paid_sns_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    social_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=320)
    waiting_unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1000)
    energy_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=25)
    energy_full_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)
    license_live_energy_recoverly_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=60)
    energy_full_need_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    over_max_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    training_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=3)
    training_energy_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=3)
    friend_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=10)
    invite_code: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0, index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)
    update_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)
    tutorial_state: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    active_deck_index: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)

    active_background: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    active_award: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)

    def set_passwd(self, passwd: str):
        salt = util.randbytes(SALT_SIZE)
        hmac_hash = hmac.new(salt, passwd.encode("UTF-8"), digestmod=hashlib.sha512).digest()
        result = salt + hmac_hash[SALT_SIZE:]
        self.passwd = str(base64.b64encode(result), "UTF-8")

    def check_passwd(self, passwd: str):
        if self.passwd is None:
            return False
        result = base64.b64decode(self.passwd)
        salt = result[:SALT_SIZE]
        hmac_hash = hmac.new(salt, passwd.encode("UTF-8"), digestmod=hashlib.sha512).digest()
        return result[SALT_SIZE:] == hmac_hash[SALT_SIZE:]

    @property
    def friend_id(self):
        return "%09d" % self.invite_code


class Background(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    background_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)


class Award(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    award_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)


class TOSAgree(common.Base):
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), primary_key=True
    )


class Unit(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    active: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(index=True)
    favorite_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    is_signed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)

    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    skill_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    max_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    love: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)  # Bond
    rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Non-idolized = 1, idolized = 2
    display_rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Same as rank
    level_limit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_removable_skill_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitDeck(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    deck_number: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, deck_number),)


class UnitDeckPosition(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    deck_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(UnitDeck.id), index=True
    )
    position: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Unit.id), index=True
    )

    __table_args__ = (sqlalchemy.UniqueConstraint(deck_id, unit_id),)


class UnitSupporter(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, unit_id),)


class Album(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    rank_max_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    love_max_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    rank_level_max_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    highest_love_per_unit: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    favorite_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    sign_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)


class UnitCenter(common.Base):
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), primary_key=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Unit.id), index=True
    )


class Achievement(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    achievement_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    achievement_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    is_accomplished: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default=util.time, index=True
    )
    end_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0, index=True)
    is_new: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=True, index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(achievement_id, user_id),)


class LiveEffort(common.Base):
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), primary_key=True
    )
    live_effort_point_box_spec_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    current_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)


class LoginBonus(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id)
    )
    year: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    month: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    day: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, year, month, day),)


class Incentive(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    add_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    message: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()  # JSON-data
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default=util.time, index=True
    )
    expire_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0, index=True)

    def set_message(self, message_jp: str | tuple[str, str | None], message_en: str | None):
        if isinstance(message_jp, tuple):
            message_jp, message_en = message_jp

        result = {const.INCENTIVE_MESSAGE_NAME: message_jp}
        if message_en is not None:
            result[const.INCENTIVE_MESSAGE_NAME_EN] = message_en

        self.message = json.dumps(result, separators=(",", ":"))

    def get_message(self, language: idoltype.Language):
        message: dict[str, str] = json.loads(self.message)

        if language == idoltype.Language.en:
            return message.get(const.INCENTIVE_MESSAGE_NAME_EN, message[const.INCENTIVE_MESSAGE_NAME])
        else:
            return message[const.INCENTIVE_MESSAGE_NAME]


class IncentiveUnitOption(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Incentive.id), primary_key=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()

    is_signed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    skill_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    max_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    love: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)  # Bond
    rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Non-idolized = 1, idolized = 2
    display_rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Same as rank
    level_limit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_removable_skill_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class Scenario(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    scenario_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    completed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)


class SubScenario(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    subscenario_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    completed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)


class LiveClear(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    live_difficulty_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    hi_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    hi_combo_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    clear_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, live_difficulty_id),)


class MuseumUnlock(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    museum_contents_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, museum_contents_id),)


engine = sqlalchemy.ext.asyncio.create_async_engine(config.get_database_url())
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)


def get_sessionmaker():
    global sessionmaker
    return sessionmaker

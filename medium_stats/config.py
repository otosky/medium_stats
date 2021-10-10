import os
from dataclasses import dataclass

import dotenv
import lazy_object_proxy


def get_env_var_or_raise(key: str):
    env_var = os.environ.get(key)
    if not env_var:
        raise KeyError(f"Environment variable not set: {key}")
    return env_var


@dataclass
class PublicationConfig:
    sid: str
    uid: str
    slug: str

    @staticmethod
    def from_env():
        dotenv.load_dotenv()
        sid = get_env_var_or_raise("MEDIUM_SID")
        uid = get_env_var_or_raise("MEDIUM_UID")
        slug = get_env_var_or_raise("MEDIUM_PUBLICATION_SLUG")
        return PublicationConfig(sid=sid, uid=uid, slug=slug)

    def as_dict(self):
        return self.__dict__


publication_config = lazy_object_proxy.Proxy(lambda: PublicationConfig.from_env())


@dataclass
class UserConfig:
    sid: str
    uid: str
    username: str

    @staticmethod
    def from_env():
        dotenv.load_dotenv()
        sid = get_env_var_or_raise("MEDIUM_SID")
        uid = get_env_var_or_raise("MEDIUM_UID")
        username = get_env_var_or_raise("MEDIUM_USERNAME")
        return UserConfig(sid=sid, uid=uid, username=username)

    def as_dict(self):
        return self.__dict__


user_config = lazy_object_proxy.Proxy(lambda: UserConfig.from_env())

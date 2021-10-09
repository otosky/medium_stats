# cookie_fetcher
# usage = "medium-stats fetch_cookies -u USERNAME --email EMAIL (--pwd PWD | --pw-in-env)"
# cf = subparser.add_parser(
#     "fetch_cookies",
#     usage=usage,
#     help="log in to Medium via Selenium and extract session cookies",
# )
# cf.add_argument("-u", metavar="HANDLE", help="Medium username")
# login = cf.add_argument_group("login")
# login.add_argument("--email", metavar="EMAIL", help="login method email", required=True)
# pwd_group = login.add_mutually_exclusive_group(required=True)
# pwd_group.add_argument("--pwd", metavar="PWD", help="login method password")
# pwd_group.add_argument(
#     "--pwd-in-env",
#     action="store_true",
#     help="pulls Medium password from environment variable",
# )
# cf.add_argument(
#     "--creds",
#     default=default_creds,
#     help='creds.ini file path with "sid" and "uid" values',
# )


class MediumConfigHelper:
    def __init__(self, config_path, account_name):

        self.handle = account_name
        self.cookies = MediumConfigHelper._retrieve_cookies(config_path, account_name)
        self.sid = self.cookies["sid"]
        self.uid = self.cookies["uid"]

    @staticmethod
    def _validate_config(config_path, account_name):
        """
        Checks to see if config file has correct sections:
        [account_name]
        sid = sid_here
        uid = uid_here
        """

        config = configparser.ConfigParser()
        config.read(config_path)
        section = config.has_section(account_name)
        if not section:
            raise ValueError(f'Account name "{account_name}" not found in section headers')
        options = ["sid", "uid"]
        option_exists = [config.has_option(account_name, opt) for opt in options]
        if sum(option_exists) < len(options):
            raise ValueError("Config file not properly formed")

        return config

    @classmethod
    def _retrieve_cookies(cls, config_path, account_name):

        config_exists = os.path.exists(config_path)
        if not config_exists:
            raise ValueError("Config file does not exist")

        config = cls._validate_config(config_path, account_name)
        cookies = config[account_name]

        return dict(cookies)

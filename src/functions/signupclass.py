from functools import partial
import json
import os
import pickle
import time
import requests
from datareq.datatypes.Creds import Creds
import datareq.datatypes.monad as Monad
from datareq.sso import get_icsid, login
from datareq.utils.generate import generate_unique

from datareq.utils.util import get_classes, get_statenum


class SessionWrapper:
    def __init__(self, cred: Creds):
        self.s = requests.Session()
        self.s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )
        self.c = cred

    def save(self, path=""):
        os.makedirs("cache", exist_ok=True)
        with open(f"cache/save_{path}.pkl", "wb") as f:
            pickle.dump(self.s, f)
        with open(f"cache/save_{path}.json", "w") as f:
            json.dump(
                {
                    "time": str(time.time()),
                    "user": self.c.user,
                    "password": self.c.password,
                    "ICSID": self.c.ICSID,
                },
                f,
            )

    @classmethod
    def load(cls, path="") -> Monad.Option:
        try:
            with open(f"cache/save_{path}.pkl", "rb") as f:
                s = pickle.load(f)
            with open(f"cache/save_{path}.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return Monad.Err("failed to load")
        cred = Creds(data["user"], data["password"])
        cred.ICSID = data["ICSID"]
        a = cls(cred)
        a.s = s
        return Monad.Ok(a)

    @classmethod
    def try_login(cls, c: Creds):
        instance = cls.load(path=f"{c.user}-{c.password}")
        if isinstance(instance, Monad.Ok):
            try:
                instance.unwrap().setup_cart()  # if this fails our instance has expired
                return instance.unwrap()
            except TypeError:
                pass
        print(f"relogging in for {c.user}")
        # if fails top, we must re log in necessarily
        instance = SessionWrapper(c)
        instance.get_creds()
        instance.get_icsid()
        instance.save(path=f"{c.user}-{c.password}")
        classes = instance.setup_cart()  # if this fails i have no clue
        return instance

    def get_state(self, url, err="Failed to get state") -> Monad.Option:
        response = self.s.get(url)
        try:
            statenum = get_statenum(response.text)
        except AttributeError:
            return Monad.Err(err)
        return Monad.Ok((statenum, response))

    def post_state(self, url, err="", **kwargs) -> Monad.Option:
        response = self.s.post(url, **kwargs)
        try:
            statenum = get_statenum(response.text)
        except AttributeError:
            return Monad.Err(err)
        return Monad.Ok((statenum, response))

    def get_creds(self):
        login(self.s, self.c.user, self.c.password)

    def get_icsid(self):
        self.c.ICSID = Monad.Ok(self.c).bind(partial(get_icsid, self.s)).unwrap()

    def setup_cart(self) -> dict[str, int]:
            # returns list of classes, and updates statenum
            self.c.statenum, response = self.get_state(
                f"https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL"
            ).unwrap()
            self.c.statenum, response = self.post_state(
                "https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
                err="failed to select year",
                params=generate_unique(
                    self.c, "DERIVED_SSS_SCT_SSR_PB_GO", {"SSR_DUMMY_RECV1$sels$1$$0": "1"}
                ),
            ).unwrap()
            return get_classes(response.text)
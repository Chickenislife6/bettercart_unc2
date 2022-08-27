from dataclasses import dataclass
from functools import partial
import json
import pickle
import re
import time
from bs4 import BeautifulSoup
import requests
from datareq.datatypes.Creds import Creds
from datareq.datatypes.monad import Ok
import datareq.datatypes.monad as Monad
from datareq.sso import get_icsid, login
from datareq.utils.generate import generate_delete, generate_enroll, generate_generic, generate_lookup, generate_swap
from datareq.utils.util import get_classes, get_statenum, save_to_file
from concurrent.futures import ThreadPoolExecutor
import concurrent
import concurrent.futures

class SignUpHelper:
    def __init__(self, cred: Creds):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0", "Accept-Language": "en-US,en;q=0.5"})
        self.c = cred

    def save(self, path = ""):
        with open(f'cache/save_{path}.pkl', 'wb') as f:
            pickle.dump(self.s, f)
        with open(f'cache/save_{path}.json', 'w') as f:
            json.dump({"time": str(time.time()), "user": self.c.user, "password": self.c.password, "ICSID": self.c.ICSID}, f)


    @classmethod
    def load(cls, path= "") -> Monad.Option:
        try:
            with open(f'cache/save_{path}.pkl', 'rb') as f:
                s = pickle.load(f)
            with open(f'cache/save_{path}.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return Monad.Err("failed to load")
        cred = Creds(data['user'], data['password'])
        cred.ICSID = data['ICSID']
        a = cls(cred)
        a.s = s
        return Monad.Ok(a)

    
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

    def check_class(self, class_ids):
        # MUST CONSUME ALL ENTRIES
        self.c.statenum, response = self.post_state(
            url = "https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params = generate_generic(self.c, "DERIVED_REGFRM1_SSR_PB_SRCH")
        ).unwrap()
        self.delete_garbage(response.text)
        save_to_file(response.text, "test.html")
        print(response.request.url)
        print(response.request.body)
        print(response.request.headers)
        def check_class(cls: SignUpHelper, class_id: int):
            response = self.s.post(
                url = "https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
                params = generate_lookup(cls.c, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH", class_id)
            )
            pattern = re.compile(r'PS_CS_STATUS_([^_]*)_ICN')
            save_to_file(response.text, f"id{class_id}.html")
            print(pattern.findall(response.text))
            status = pattern.findall(response.text)[-1]
            if status == 'OPEN':
                return (True, class_id)
            if status == 'CLOSED' or status == 'WAITLIST':
                return (False, class_id)
            raise "you're not supposed to be here!"

        save_to_file(response.text, "whybreak.html")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = (executor.submit(check_class, self, class_id) for class_id in class_ids)
            for future in concurrent.futures.as_completed(futures):
                yield future.result()
                
        self.c.statenum = int(self.c.statenum) + 1 # magic number
        response = self.s.post( # does not update state number, just resets search
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params=generate_generic(self.c, "#ICCancel")
        )
        self.c.statenum = int(self.c.statenum) + 1


    def setup_cart(self) -> dict[str, int]:
        # returns list of classes, and updates statenum
        self.c.statenum, response = self.get_state(f"https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL").unwrap()
        return get_classes(response.text)


    def register_in_classes(self, indices: list):
        body = generate_enroll(self.c, indices, action="DERIVED_REGFRM1_LINK_ADD_ENRL")
        response = self.s.post(
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params=body
        )
        save_to_file(response.text, 'test.txt')
        pattern = re.compile(r'ENRL_REQUEST_ID=(\d+)')
        cart_id = pattern.search(response.text).group(1)

        self.c.statenum, response = self.get_state(f"https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_ADD.GBL?Action=U&ENRL_REQUEST_ID={cart_id}").unwrap()
        save_to_file(response.text, "a.html")
        
        self.c.statenum, response = self.post_state(
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_ADD.GBL",
            params=generate_generic(self.c, "DERIVED_REGFRM1_SSR_PB_SUBMIT"),
        ).unwrap()
        save_to_file(response.text, "b.html")
        return response.text


    def swap(self, class1, class2):
        self.c.statenum, response = self.get_state("https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL?Page=SSR_SSENRL_SWAP&Action=A&ACAD_CAREER=UGRD&ENRL_REQUEST_ID=&INSTITUTION=UNCCH&STRM=2229").unwrap()

        params = generate_swap(self.c, class1, class2, "DERIVED_REGFRM1_SSR_PB_ADDTOLIST1$184$")
        self.c.statenum, response = self.post_state(
            url = "https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL",
            params = params
        ).unwrap()
        
        self.c.statenum, response = self.post_state(
            url = "https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL",
            params = generate_generic(self.c, "DERIVED_REGFRM1_SSR_PB_SUBMIT")
        ).unwrap()

        return response.text
    
    
    def delete_garbage(self, text:str):
        # depreciated since I found out you could add a header
        soup = BeautifulSoup(text, 'html.parser')
        pattern = re.compile(r'NC_CSE_ATTR_VW_DESCR.*')
        elts = soup.find_all('span', {"id": pattern})
        for elt in elts:
            if elt.text.strip() == "":
                continue
            print(elt.text)
            attr = elt.text.strip().split(" ")[0]
            self.c.statenum, response = self.post_state(
                url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
                params=generate_delete(self.c, attr, "NC_CSE_ATTR_TBL$delete$0$$0")
            ).unwrap()
            save_to_file(response.text, "deleted.html")

    @classmethod
    def try_login(cls, c: Creds):
      instance = cls.load(path=f"{c.user}-{c.password}")
      if isinstance(instance, Monad.Ok):
        try:
          instance.unwrap().setup_cart() # if this fails our instance has expired
          return instance.unwrap()
        except TypeError:
          pass
      # if fails top, we must re log in necessarily
      instance = SignUpHelper(c)
      instance.get_creds()
      instance.get_icsid()
      instance.save(path=f"{c.user}-{c.password}")
      classes = instance.setup_cart() # if this fails i have no clue
      return instance

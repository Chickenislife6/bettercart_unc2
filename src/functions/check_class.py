# DEPRECIATED
# DEPRECIATED
# DEPRECIATED

import re
from datareq.utils.generate import (
    generate_delete,
    generate_generic,
    generate_lookup,
)
from concurrent.futures import ThreadPoolExecutor
import concurrent
import concurrent.futures
from bs4 import BeautifulSoup
from datareq.utils.util import save_to_file
from functions.signupclass import SessionWrapper


def delete_garbage(instance: SessionWrapper, text: str):
    # depreciated since I found out you could add a header
    soup = BeautifulSoup(text, "html.parser")
    pattern = re.compile(r"NC_CSE_ATTR_VW_DESCR.*")
    elts = soup.find_all("span", {"id": pattern})
    for elt in elts:
        if elt.text.strip() == "":
            continue
        print(elt.text)
        attr = elt.text.strip().split(" ")[0]
        instance.c.statenum, _ = instance.post_state(
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params=generate_delete(instance.c, attr, "NC_CSE_ATTR_TBL$delete$0$$0"),
        ).unwrap()


def check_class(instance: SessionWrapper, class_ids):
    # MUST CONSUME ALL ENTRIES
    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_generic(instance.c, "DERIVED_REGFRM1_SSR_PB_SRCH"),
    ).unwrap()
    delete_garbage(instance, response.text)

    def check_class(cls: SessionWrapper, class_id: int):
        response = instance.s.post(
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params=generate_lookup(
                cls.c, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH", class_id
            ),
        )
        pattern = re.compile(r"PS_CS_STATUS_([^_]*)_ICN")
        status = pattern.findall(response.text)[-1]
        if status == "OPEN":
            return (True, class_id)
        if status == "CLOSED" or status == "WAITLIST":
            return (False, class_id)
        raise "you're not supposed to be here!"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = (
            executor.submit(check_class, instance, class_id) for class_id in class_ids
        )
        for future in concurrent.futures.as_completed(futures):
            yield future.result()

    instance.c.statenum = int(instance.c.statenum) + 1  # magic number
    response = instance.s.post(  # does not update state number, just resets search
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_generic(instance.c, "#ICCancel"),
    )
    instance.c.statenum = int(instance.c.statenum) + 1

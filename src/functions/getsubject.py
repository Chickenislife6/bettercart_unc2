import copy
import gc
from datareq.utils.generate import (
    generate_generic,
    generate_subject_lookup,
)
from bs4 import BeautifulSoup
from functions.signupclass import SessionWrapper

import os, psutil
process = psutil.Process(os.getpid())


def get_cart(instance: SessionWrapper, subject, var: bool, attribute: str):
    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_generic(instance.c, "DERIVED_REGFRM1_SSR_PB_SRCH"),
    ).unwrap()

    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_subject_lookup(instance.c, subject, var, attribute),
    ).unwrap()

    soup = BeautifulSoup(response.text, "lxml")
    try:
        num_classes = int(
            soup.find("td", attrs={"class": "PSGROUPBOXLABEL"}).string.split(" ")[0]
        )
    except ValueError:
        num_classes = 0

    result = {}

    for i in range(num_classes):
        _, response = instance.post_state(
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params=generate_generic(instance.c, f"MTG_CLASSNAME${i}"),
        ).unwrap()
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.find("span", id="DERIVED_CLSRCH_DESCR200").string[:]
        class_num = soup.find("span", id="SSR_CLS_DTL_WRK_CLASS_NBR").string[:]
        open = soup.find("span", id="NC_RC_OPEX_WRK_DESCR1$0").string[:]
        reserved = soup.find("span", id="NC_RC_OPEX_WRK_DESCR1$1").string[:]
        waitlist = soup.find("span", id="NC_RC_OPEX_WRK_DESCR1$311$$0").string[:]
        try:
            attribute = ""
            for i in soup.find("span", id="SSR_CLS_DTL_WRK_SSR_CRSE_ATTR_LONG").children:
                i = i.text.strip()
                if i == "":
                    attribute += "\n"
                else:
                    attribute += i
        except AttributeError:
            attribute = ""

        try:
            description = soup.find("span", id="DERIVED_CLSRCH_DESCRLONG").string[:]
        except AttributeError:
            description = ""

        try: 
            name = name + ": " + soup.find("span", id="MTG_TOPIC$0").string[:]
        except:
            pass
        time = soup.find("span", id="MTG_SCHED$0").string[:]
        try:
            prof = soup.find("span", id="MTG_INSTR$0").string[:]
        except:
            prof = "N/A"

        result[class_num] = (name, open, reserved, waitlist, time, prof, description, attribute)

        print(process.memory_info().rss)
        gc.collect()

    response = instance.s.post(  # does not update state number, just resets search
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_generic(instance.c, "#ICCancel"),
    )

    instance.c.statenum = int(instance.c.statenum) + 1

    return result

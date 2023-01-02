from datareq.utils.generate import (
    generate_generic,
    generate_subject_lookup,
)
from bs4 import BeautifulSoup
from functions.signupclass import SessionWrapper


def get_cart(instance: SessionWrapper, subject):
    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_generic(instance.c, "DERIVED_REGFRM1_SSR_PB_SRCH"),
    ).unwrap()

    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_subject_lookup(instance.c, subject),
    ).unwrap()

    soup = BeautifulSoup(response.text, "lxml")
    num_classes = int(
        soup.find("td", attrs={"class": "PSGROUPBOXLABEL"}).string.split(" ")[0]
    )

    result = {}

    for i in range(num_classes):
        _, response = instance.post_state(
            url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
            params=generate_generic(instance.c, f"MTG_CLASSNAME${i}"),
        ).unwrap()
        soup = BeautifulSoup(response.text, "lxml")
        name = soup.find("span", id="DERIVED_CLSRCH_DESCR200").string
        class_num = soup.find("span", id="SSR_CLS_DTL_WRK_CLASS_NBR").string
        open = soup.find("span", id="NC_RC_OPEX_WRK_DESCR1$0").string
        reserved = soup.find("span", id="NC_RC_OPEX_WRK_DESCR1$1").string
        waitlist = soup.find("span", id="NC_RC_OPEX_WRK_DESCR1$311$$0").string
        print(class_num)
        result[class_num] = (name, open, reserved, waitlist)

    response = instance.s.post(  # does not update state number, just resets search
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=generate_generic(instance.c, "#ICCancel"),
    )

    instance.c.statenum = int(instance.c.statenum) + 1

    return result

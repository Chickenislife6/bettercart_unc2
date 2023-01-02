import re
from datareq.utils.generate import (
    generate_enroll,
    generate_generic,
)
from datareq.utils.util import save_to_file
from functions.signupclass import SessionWrapper


def register_in_classes(instance: SessionWrapper, indices: list):
    body = generate_enroll(instance.c, indices, action="DERIVED_REGFRM1_LINK_ADD_ENRL")
    response = instance.s.post(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL",
        params=body,
    )
    save_to_file(response.text, "register_bad")
    pattern = re.compile(r"ENRL_REQUEST_ID=(\d+)")
    try:
        cart_id = pattern.search(response.text).group(1)
    except AttributeError:
        return "Please come back with a proper enrollment session"

    instance.c.statenum, response = instance.get_state(
        f"https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_ADD.GBL?Action=U&ENRL_REQUEST_ID={cart_id}"
    ).unwrap()

    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_ADD.GBL",
        params=generate_generic(instance.c, "DERIVED_REGFRM1_SSR_PB_SUBMIT"),
    ).unwrap()

    return response.text

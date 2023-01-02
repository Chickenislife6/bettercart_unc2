from datareq.utils.generate import (
    generate_generic,
    generate_swap,
)
from functions.signupclass import SessionWrapper

def swap(instance: SessionWrapper, class1, class2):
    instance.c.statenum, response = instance.get_state(
        "https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL?Page=SSR_SSENRL_SWAP&Action=A&ACAD_CAREER=UGRD&ENRL_REQUEST_ID=&INSTITUTION=UNCCH&STRM=2232"
    ).unwrap()

    params = generate_swap(
        instance.c, class1, class2, "DERIVED_REGFRM1_SSR_PB_ADDTOLIST1$184$"
    )
    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL",
        params=params,
    ).unwrap()

    instance.c.statenum, response = instance.post_state(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL",
        params=generate_generic(instance.c, "DERIVED_REGFRM1_SSR_PB_SUBMIT"),
    ).unwrap()

    return response.text

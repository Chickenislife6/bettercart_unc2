from datareq.datatypes.Creds import Creds


def generate_enroll(c: Creds, indices, action):
    # must run cart_setup before, probably
    data = {
        "ICStateNum": c.statenum,
        "ICAction": action,
        "ICSID": c.ICSID,
    }
    for i, Bool in enumerate(indices):
        if Bool:
            data[f"P_SELECT$chk${i}"] = "Y"
            data[f"P_SELECT${i}"] = "Y"
        else:
            data[f"P_SELECT$chk${i}"] = "N"
    return data


def generate_swap(c: Creds, c1, c2, action):
    data = {
        "ICStateNum": c.statenum,
        "ICAction": action,
        "ICSID": c.ICSID,
        "DERIVED_REGFRM1_DESCR50$225$": c1,
        "DERIVED_REGFRM1_SSR_CLASSNAME_35$183$": c2,
    }
    return data


def generate_unique(c: Creds, action, data):
    data1 = generate_generic(c, action)
    data1.update(data)
    return data1


def generate_generic(c: Creds, action):
    data = {
        "ICStateNum": c.statenum,
        "ICAction": action,
        "ICSID": c.ICSID,
    }
    return data


def generate_subject_lookup(c: Creds, subject: str, gt: bool, attribute: str):
    var = "T"
    if gt:
        var = "G"
    data = {
        "ICStateNum": c.statenum,

        "ICAction": "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH",
        "ICSID": c.ICSID,
        "SSR_CLSRCH_WRK_CATALOG_NBR$1": "500",
        "SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1": var,
        "SSR_CLSRCH_WRK_SUBJECT$0": subject,
        "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$chk$3": "N",
        "SSR_CLSRCH_WRK_INCLUDE_CLASS_DAYS$5":"J",
        "SSR_CLSRCH_WRK_MON$chk$5":"Y",
        "SSR_CLSRCH_WRK_MON$5":"Y",
        "SSR_CLSRCH_WRK_TUES$chk$5":"Y",
        "SSR_CLSRCH_WRK_TUES$5":"Y",
        "SSR_CLSRCH_WRK_WED$chk$5":"Y",
        "SSR_CLSRCH_WRK_WED$5":"Y",
        "SSR_CLSRCH_WRK_THURS$chk$5":"Y",
        "SSR_CLSRCH_WRK_THURS$5":"Y",
        "SSR_CLSRCH_WRK_FRI$chk$5":"Y",
        "SSR_CLSRCH_WRK_FRI$5":"Y",
        "SSR_CLSRCH_WRK_SAT$chk$5":"Y",
        "SSR_CLSRCH_WRK_SAT$5":"Y",
        "SSR_CLSRCH_WRK_SUN$chk$5":"Y",
        "SSR_CLSRCH_WRK_SUN$5":"Y",
        "SSR_CLSRCH_WRK_SSR_EXACT_MATCH2$6":"B",
        "SSR_CLSRCH_WRK_SSR_UNITS_MAX_OPR$9": "LE",
        "SSR_CLSRCH_WRK_UNITS_MAXIMUM$9": "18"
    }
    if attribute: 
        data["NC_CSE_ATTR_TBL_CRSE_ATTR_VALUE$0"] = attribute
    return data


def generate_lookup(c: Creds, action: str, class_num):
    data = {
        "ICStateNum": c.statenum,
        "ICAction": action,
        "ICSID": c.ICSID,
        "NC_CSE_ATTR_TBL_CRSE_ATTR_VALUE$0": "",
        "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$chk$3": "N",
        "SSR_CLSRCH_WRK_CLASS_NBR$8": str(class_num),
        "SSR_CLSRCH_WRK_SSR_UNITS_MAX_OPR$9": "LE",
        "SSR_CLSRCH_WRK_UNITS_MAXIMUM$9": "18",
    }
    return data


def generate_delete(c: Creds, name: str, action: str):
    data = {
        "ICStateNum": c.statenum,
        "ICAction": action,
        "ICSID": c.ICSID,
        "NC_CSE_ATTR_TBL_CRSE_ATTR_VALUE$0": name,
        "SSR_CLSRCH_WRK_SUBJECT$0": "",
        "SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1": "E",
        "SSR_CLSRCH_WRK_CATALOG_NBR$1": "",
        "SSR_CLSRCH_WRK_ACAD_CAREER$2": "",
        "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$chk$3": "Y",
        "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3": "Y",
    }
    return data

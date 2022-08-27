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
    "DERIVED_REGFRM1_DESCR50$225$":	c1,
    "DERIVED_REGFRM1_SSR_CLASSNAME_35$183$": c2,
    }
    return data

def generate_generic(c: Creds, action):
    data = {
    "ICStateNum": c.statenum,
    "ICAction": action,
    "ICSID": c.ICSID,
    }
    return data

def generate_lookup(c: Creds, action: str, class_num):
    data = {
    "ICStateNum": c.statenum,
    "ICAction": action,
    "ICSID": c.ICSID,
    "NC_CSE_ATTR_TBL_CRSE_ATTR_VALUE$0": "",
    "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$chk$3":"N",
    "SSR_CLSRCH_WRK_CLASS_NBR$8": str(class_num),
    "SSR_CLSRCH_WRK_SSR_UNITS_MAX_OPR$9":"LE",
    "SSR_CLSRCH_WRK_UNITS_MAXIMUM$9": "18",
    }
    return data

def generate_delete(c: Creds, name: str, action:str):
    data = {
    "ICStateNum": c.statenum,
    "ICAction": action,
    "ICSID": c.ICSID,
    "NC_CSE_ATTR_TBL_CRSE_ATTR_VALUE$0":name,
    "SSR_CLSRCH_WRK_SUBJECT$0":	"",
    "SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1":	"E",
    "SSR_CLSRCH_WRK_CATALOG_NBR$1":	"",
    "SSR_CLSRCH_WRK_ACAD_CAREER$2":	"",
    "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$chk$3":	"Y",
    "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3":	"Y"
    }
    return data
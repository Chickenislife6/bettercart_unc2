import json
import pickle
import sys
import requests
import os
from bs4 import BeautifulSoup
import requests.utils
from datareq.datatypes.Creds import Creds
from datareq.datatypes.monad import Err, Ok, Option
from datareq.utils.util import get_saml, get_statenum
from datareq.utils.util import save_to_file




def login(s: requests.Session, user, password):
    # grabs SAMLRequest
    SAMLRequest = get_saml(
        s.get(
            url="https://pa.cc.unc.edu/psp/paprd/EMPLOYEE/EMPL/h/?tab=NC_REDIRECT&TargetPage=PortalHome",
        ).text,
        "SAMLRequest")

    # gets cookies for SSO page
    s.post(
            url="https://sso.unc.edu/idp/profile/SAML2/POST/SSO",
            params={"SAMLRequest":SAMLRequest}
        )

    # SSO Page login 
    body = {
        "j_username": user,
        "j_password": password,
        "_eventId_proceed": ""
    }
    SAMLResponse = get_saml(s.post(
        url="https://sso.unc.edu/idp/profile/SAML2/POST/SSO?execution=e1s1",
        params=body
    ).text,
    "SAMLResponse")
    
    # grab cookies for authentitation
    s.post(
        url="https://pa.cc.unc.edu/Shibboleth.sso/SAML2/POST",
        data={"SAMLRequest": SAMLResponse,
        "RelayState": "https://pa.cc.unc.edu/psp/paprd/EMPLOYEE/EMPL/h/?tab=NC_REDIRECT&TargetPage=PortalHome"
        }
    )

    #get second samlrequest
    SAMLRequest = get_saml(s.get(
        url="https://cs.cc.unc.edu/Shibboleth.sso/Login",
    ).text, 
    "SAMLRequest")

    #get second samlresponse
    SAMLResponse = get_saml(s.post(
        url="https://sso.unc.edu/idp/profile/SAML2/POST/SSO",
        data={"SAMLRequest": SAMLRequest}
    ).text,
    "SAMLResponse")

    # get second shibsession
    s.post(
        url="https://cs.cc.unc.edu/Shibboleth.sso/SAML2/POST",
        data={"SAMLResponse": SAMLResponse}
    )

    # get csprd thingy?
    s.get(
        url="https://cs.cc.unc.edu/psc/campus/?cmd=ping",
    )

def get_icsid(s: requests.Session, c: Creds) -> Option:
    response = s.get(
        url="https://pa.cc.unc.edu/psp/paprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL",
    )
    response = s.get(
        url="https://cs.cc.unc.edu/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?PortalActualURL=https%3a%2f%2fcs.cc.unc.edu%2fpsc%2fcampus%2fEMPLOYEE%2fSA%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentURL=https%3a%2f%2fcs.cc.unc.edu%2fpsc%2fcampus%2fEMPLOYEE%2fSA%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&PortalContentProvider=SA&PortalCRefLabel=Student%20Center&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fpa.cc.unc.edu%2fpsp%2fpaprd%2f&PortalURI=https%3a%2f%2fpa.cc.unc.edu%2fpsc%2fpaprd%2f&PortalHostNode=EMPL&NoCrumbs=yes"
    )
    soup = BeautifulSoup(response.content, 'html.parser')
    elt = soup.find('input', {'id':'ICSID'})
    if elt == None:
        return Err("Failed to obtain ICSID")
    ICSID = elt['value']
    c.ICSID = elt['value']

    return Ok(ICSID)



if __name__ == "__main__":
    s = requests.Session()
    if sys.argv[1] == "load":
        with open('cache/save.pkl', 'rb') as f:
            s = pickle.load(f)
    else:
        login(s)
    ICSID = get_icsid(s)


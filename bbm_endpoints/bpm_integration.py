import requests
import json
import logging

_logger = logging.getLogger(__name__)


def get_bpm_access(bpm_url):
    url = "{}/bonita/loginservice".format(bpm_url)
    payload = 'username=walter.bates&password=bpm'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 204:
        token = response.cookies.get("X-Bonita-API-Token")
        tenant = response.cookies.get("bonita.tenant")
        bos_local = response.cookies.get("BOS_Locale")
        session_id = response.cookies.get("JSESSIONID")
        cookies = 'bonita.tenant=%s; BOS_Locale=%s; JSESSIONID=%s; X-Bonita-API-Token=%s' % (
            tenant, bos_local, session_id, token)
        return {'cookies': cookies,
                'token': token}

    else:
        _logger.warning("Access Fail to BPM Server.")
        return False

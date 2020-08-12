# Create your tasks here
from __future__ import absolute_import, unicode_literals
from .models import *
from celery import shared_task
from celery.task import periodic_task
from datetime import timedelta
import requests
import re
import json


#@periodic_task(run_every=(timedelta(seconds=30)), name='hello_worker')
#def hello():
#    print("worker is active.")


@shared_task
def check_health():
    rules = HealthCheckRule.objects.filter(enable=True)
    print("health check starts to run " + str(rules.count()) + " rules")

    for rule in rules:
        make_http_call.delay(rule.id)


@shared_task
def make_http_call(rule_id):
    rule = HealthCheckRule.objects.get(id=rule_id)
    error = False
    error_description = ""
    cert = None
    success = False
    url = rule.url

    try:
        if rule.client_certificate:
            cert_file_path = rule.client_certificate.client_cert.path
            if rule.client_certificate.client_key:
                key_file_path = rule.client_certificate.client_key.path
                cert = (cert_file_path, key_file_path)
            else:
                cert = cert_file_path
        headers = {}
        for header in rule.headers.all():
            headers[header.key] = header.value
    
        if rule.http_method == 'get':
            r = requests.get(url, cert=cert, headers=headers, verify=False)
        elif rule.http_method == 'post':
            try:
                data = json.loads(rule.request_body)
                data = json.dumps(data)
            except:
                data = rule.request_body

            r = requests.post(url, data=data, cert=cert, headers=headers, verify=False)
        else:
            pass

        try:
            payload = json.dumps(r.json(), sort_keys=True)
        except:
            payload = str(r.content)

        try:
            expected_response_body = json.dumps(json.loads(rule.expected_response_body), sort_keys=True)
        except:
            expected_response_body = rule.expected_response_body

        try:
            payload_match = re.search(expected_response_body, payload)
        except:
            payload_match = re.search(re.escape(expected_response_body), payload)

        code_match = re.search(rule.expected_response_code, str(r.status_code))
        if payload_match and code_match:
            success = True
        else:
            error = True
            error_description = "Status code or payload doesn't match to the expected ones!"

        HealthCheckRecord.objects.create(response_code=r.status_code,
                                         response_body=payload,
                                         response_delay=float(r.elapsed.seconds + r.elapsed.microseconds / 1000000),
                                         health_check_rule=rule,
                                         success=success,
                                         error=error, 
                                         error_description=error_description)

    except Exception as e:
        error = True
        error_description = str(e)
        HealthCheckRecord.objects.create(health_check_rule=rule, success=False, 
                                         error=error, error_description=error_description)

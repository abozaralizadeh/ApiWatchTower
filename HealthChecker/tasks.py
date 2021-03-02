# Create your tasks here
from __future__ import absolute_import, unicode_literals
from .models import *
from celery import shared_task
from celery.task import periodic_task
from datetime import datetime, timedelta
import requests
import re
import json
import redis
from django.conf import settings

r = redis.Redis(host=settings.AWT_REDIS_HOST, port=settings.AWT_REDIS_PORT, db=1, decode_responses=True)


@shared_task
def clean_record(days):
    records = HealthCheckRecord.objects.filter(timestamp__lte=datetime.now() - timedelta(days=days))
    records.delete()


@shared_task
def check_health():
    heads = set()
    seen = []
    rules = HealthCheckRule.objects.filter(enable=True)
    print("Health check starts to run " + str(rules.count()) + " rules")

    dependent_rules = rules.filter(run_after__isnull=False, enable=True)

    for rule in dependent_rules:
        if rule.id in seen:
            continue
        seen.append(rule.id)

        current = rule

        while current.run_after:
            current = current.run_after
            seen.append(current.id)

        heads.add(current)

    for head in heads:
        run_head_sync.s(head.id).apply_async()

    for rule in rules:
        if rule.id not in seen:
            make_http_call.s(rule.id).apply_async()


def launcher(head):
    if head.enable:
        make_http_call.s(head.id).apply_async().get(disable_sync_subtasks=False)
    nexts = head.nexts.all()

    for next in nexts:
        run_head_sync.s(next.id).apply_async()


@shared_task
def run_head_sync(rule_id):
    rule = HealthCheckRule.objects.get(id=rule_id)
    launcher(rule)


@shared_task
def make_http_call_linkable(_, rule_id):
    make_http_call(rule_id)


@shared_task
def make_http_call(rule_id):
    rule = HealthCheckRule.objects.get(id=rule_id)
    error = False
    error_description = ""
    cert = None
    success = False
    url = rule.url

    url = populate_placeholders(url)

    curl = "curl -X {} \"{}\"".format(str(rule.http_method).upper(), url)

    try:
        if rule.client_certificate:
            curl += " --key {}_key.pem --cert {}_cert.pem".format(rule.client_certificate.name.replace(' ', ''),
                                                                  rule.client_certificate.name.replace(' ', ''))
            cert_file_path = rule.client_certificate.client_cert.path
            if rule.client_certificate.client_key:
                key_file_path = rule.client_certificate.client_key.path
                cert = (cert_file_path, key_file_path)
            else:
                cert = cert_file_path
        headers = {}
        for header in rule.headers.all():
            hvalue = populate_placeholders(header.value)
            headers[header.key] = hvalue
            curl += " -H \"{}: {}\"".format(header.key, hvalue)

        if rule.http_method == 'get':
            r = requests.get(url, cert=cert, headers=headers, verify=False)
        elif rule.http_method == 'post':
            data = ''
            request_body = populate_placeholders(rule.request_body)
            try:
                data = json.loads(request_body)
                data = json.dumps(data)
            except Exception as e:
                data = request_body
            curl += " --data-raw \"{}\"".format(data)

            r = requests.post(url, data=data, cert=cert, headers=headers, verify=False)
        else:
            pass

        try:
            payload = json.dumps(r.json(), sort_keys=True)
            cache_placeholders(r.json(), rule.output_variables)
        except Exception as e:
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

        HealthCheckRecord.objects.create(request=curl,
                                         response_code=r.status_code,
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


def populate_placeholders(input):
    variables = re.findall(r'{{([a-zA-Z0-9._-]+)}}', input)
    for variable in variables:
        val = r.get(variable)
        input = input.replace('{{' + variable + '}}', str(val))

    return input


def cache_placeholders(json_payload, keys_string):
    if not keys_string:
        return
    keys_string = keys_string.replace(' ', '').replace('\n', '')
    keys = keys_string.split(',')
    for key in keys:
        name = ''
        parts = key.split('=>')
        if len(parts) == 2:
            name = parts[1]
        key = parts[0]
        ks = key.split('__')
        v = json_payload
        for k in ks:
            v = v.get(k, v)

        if name:
            r.set(name, v)
        else:
            r.set(key, v)

import demistomock as demisto
from CommonServerPython import *

''' IMPORTS '''
import requests
import tempfile

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()

''' CONSTANTS '''

ALERT_TITLE = 'Prisma Cloud Compute Alert - '
ALERT_TYPE_VULNERABILITY = 'vulnerability'
ALERT_TYPE_COMPLIANCE = 'compliance'
ALERT_TYPE_AUDIT = 'audit'
# this is a list of known headers arranged in the order to be displayed in the markdown table
HEADERS_BY_NAME = {
    'vulnerabilities': ['severity', 'cve', 'status', 'packages', 'sourcePackage', 'packageVersion', 'link'],
    'entities': ['name', 'containerGroup', 'resourceGroup', 'nodesCount', 'image', 'status', 'runningTasksCount',
                 'activeServicesCount', 'version', 'createdAt', 'runtime', 'arn', 'lastModified', 'protected'],
    'compliance': ['type', 'id', 'description']
}

''' COMMANDS + REQUESTS FUNCTIONS '''


class Client(BaseClient):
    def __init__(self, base_url, verify, project, proxy=False, ok_codes=tuple(), headers=None, auth=None):
        """
        Extends the init method of BaseClient by adding the arguments below,

        verify: A 'True' or 'False' string, in which case it controls whether we verify
            the server's TLS certificate, or a string that represents a path to a CA bundle to use.
        project: A projectID string, set in the integration parameters.
            the projectID is saved under self._project
        """

        self._project = project

        if verify in ['True', 'False']:
            super().__init__(base_url, str_to_bool(verify), proxy, ok_codes, headers, auth)
        else:
            # verify points a path to certificate
            super().__init__(base_url, True, proxy, ok_codes, headers, auth)
            self._verify = verify

    def _http_request(self, method, url_suffix, full_url=None, headers=None,
                      auth=None, json_data=None, params=None, data=None, files=None,
                      timeout=10, resp_type='json', ok_codes=None, **kwargs):
        """
        Extends the _http_request method of BaseClient.
        If self._project is available, a 'project=projectID' query param is automatically added to all requests.
        """

        # if project is given add it to params and call super method
        if self._project:
            params = params or {}
            params.update({'project': self._project})

        return super()._http_request(method=method, url_suffix=url_suffix, full_url=full_url, headers=headers,
                                     auth=auth, json_data=json_data, params=params, data=data, files=files,
                                     timeout=timeout, resp_type=resp_type, ok_codes=ok_codes, **kwargs)

    def test(self):
        """
        Calls the fetch alerts endpoint with to=epoch_time to check connectivity, authentication and authorization
        """
        return self.list_incidents(to_=time.strftime('%Y-%m-%d', time.gmtime(0)))

    def list_incidents(self, to_=None, from_=None):
        """
        Sends a request to fetch available alerts from last call
        No need to pass here TO/FROM query params, the API returns new alerts from the last request
        Can be used with TO/FROM query params to get alerts in a specific time period
        REMARK: alerts are deleted from the endpoint once were successfully fetched
        """
        params = {}
        if to_:
            params['to'] = to_
        if from_:
            params['from'] = from_

        # If the endpoint not found, fallback to the previous demisto-alerts endpoint (backward compatibility)
        try:
            return self._http_request(
                method='GET',
                url_suffix='xsoar-alerts',
                params=params
            )
        except Exception as e:
            if '[404]' in str(e):
                return self._http_request(
                    method='GET',
                    url_suffix='demisto-alerts',
                    params=params
                )
            raise e

    def api_v1_logs_defender_download_request(self, hostname, lines):
        """
        Download all logs for a certain defender
        """
        params = assign_params(hostname=hostname, lines=lines)

        headers = self._headers
        response = self._http_request('get', 'logs/defender/download', params=params, headers=headers, resp_type='response')

        return response

    def api_v1_hosts_request(self, offset, limit, search, sort, reverse,
                             collections, accountIDs, fields, hostname, distro, provider, compact, clusters):
        """
        List all available hosts
        """
        params = assign_params(offset=offset, limit=limit, search=search, sort=sort,
                               reverse=reverse, collections=collections, accountIDs=accountIDs,
                               fields=fields, hostname=hostname, distro=distro, provider=provider,
                               compact=compact, clusters=clusters)

        headers = self._headers

        response = self._http_request('get', 'hosts', params=params, headers=headers)

        return response

    def api_v1_containers_scan_request(self):
        """
        Initialize a scan on all containers.
        """
        headers = self._headers

        response = self._http_request('post', 'containers/scan', headers=headers, resp_type="text")

        return response

    def api_v1_images_names_request(self, offset, limit, search, sort, reverse, collections,
                                    accountIDs, fields, id_, hostname, repository, registry,
                                    name, layers, filterBaseImage, compact, trustStatuses, clusters):
        """
        Get all container image names
        """
        params = assign_params(offset=offset, limit=limit, search=search, sort=sort, reverse=reverse,
                               collections=collections, accountIDs=accountIDs, fields=fields, id=id_,
                               hostname=hostname, repository=repository, registry=registry, name=name,
                               layers=layers, filterBaseImage=filterBaseImage, compact=compact,
                               trustStatuses=trustStatuses, clusters=clusters)

        headers = self._headers

        response = self._http_request('get', 'images/names', params=params, headers=headers)

        return response

    def api_v1_images_request(self, offset, limit, search, sort, reverse, collections, accountIDs,
                              fields, id_, hostname, repository, registry, name, layers, filterBaseImage,
                              compact, trustStatuses, clusters):
        """
        Get details for a given image
        """
        params = assign_params(offset=offset, limit=limit, search=search, sort=sort, reverse=reverse,
                               collections=collections, accountIDs=accountIDs, fields=fields, id=id_, hostname=hostname,
                               repository=repository, registry=registry, name=name, layers=layers,
                               filterBaseImage=filterBaseImage, compact=compact, trustStatuses=trustStatuses,
                               clusters=clusters)

        headers = self._headers

        response = self._http_request('get', 'images', params=params, headers=headers)

        return response

    def api_v1_images_download_request(self, offset, limit, search, sort, reverse, collections, accountIDs,
                                       fields, id_, hostname, repository, registry, name, layers, filterBaseImage,
                                       compact, trustStatuses, clusters):

        params = assign_params(offset=offset, limit=limit, search=search, sort=sort, reverse=reverse,
                               collections=collections, accountIDs=accountIDs, fields=fields, id=id_, hostname=hostname,
                               repository=repository, registry=registry, name=name, layers=layers,
                               filterBaseImage=filterBaseImage, compact=compact, trustStatuses=trustStatuses, clusters=clusters)

        headers = self._headers

        response = self._http_request('get', 'images/download', params=params, headers=headers, resp_type="response")

        return response

    def api_v1_alert_profiles_names_request(self):
        """
        Get the alert profiles names
        """
        headers = self._headers

        response = self._http_request('get', 'alert-profiles/names', headers=headers)

        return response

    def api_v1_current_collections_request(self):
        """
        Get the current collections
        """
        headers = self._headers

        response = self._http_request('get', 'current/collections', headers=headers)

        return response

    def api_v1_defenders_image_name_request(self):
        """
        Return the full defender image name
        """
        headers = self._headers

        response = self._http_request('get', 'defenders/image-name', headers=headers)

        return response

    def api_v1_defenders_install_bundle_request(self, consoleaddr, defenderType, interpreter):
        """
        Return details on the defender install bundle
        """
        params = assign_params(consoleaddr=consoleaddr, defenderType=defenderType, interpreter=interpreter)

        headers = self._headers

        response = self._http_request('get', 'defenders/install-bundle', params=params, headers=headers)

        return response

    def api_v1_defenders_restart_request(self, id_):

        headers = self._headers

        response = self._http_request('post', f'defenders/{id_}/restart', headers=headers, resp_type="response")

        return response

    def api_v1_defenders_names_request(self, hostname, role, cluster, tasClusterIDs):
        params = assign_params(hostname=hostname, role=role, cluster=cluster, tasClusterIDs=tasClusterIDs)
        headers = self._headers

        response = self._http_request('get', 'defenders/names', params=params, headers=headers, resp_type="response")

        return response

    def api_v1_defenders_summary_request(self):
        headers = self._headers

        response = self._http_request('get', 'defenders/summary', headers=headers)

        return response

    def api_v1_deployment_host_progress_request(self):

        headers = self._headers

        response = self._http_request('get', 'deployment/host/progress', headers=headers)

        return response

    def api_v1_deployment_host_scan_request(self):

        headers = self._headers

        response = self._http_request('post', 'deployment/host/scan', headers=headers, resp_type="response")

        return response

    def api_v1_deployment_host_stop_request(self):

        headers = self._headers

        response = self._http_request('post', 'deployment/host/stop', headers=headers, resp_type="response")

        return response

    def api_v1_deployment_serverless_scan_request(self):

        headers = self._headers

        response = self._http_request('post', 'deployment/serverless/scan', headers=headers, resp_type="response")

        return response

    def api_v1_deployment_serverless_stop_request(self):

        headers = self._headers

        response = self._http_request('post', 'deployment/serverless/stop', headers=headers, resp_type="response")

        return response

    def api_v1_groups_names_request(self):

        headers = self._headers

        response = self._http_request('get', 'groups/names', headers=headers)

        return response

    def get_api_v1_users_request(self):

        headers = self._headers

        response = self._http_request('get', 'users', headers=headers)

        return response

    def get_api_v1_groups_request(self):

        headers = self._headers

        response = self._http_request('get', 'groups', headers=headers)

        return response

    def get_api_v1_projects_request(self):

        headers = self._headers

        response = self._http_request('get', 'projects', headers=headers)

        return response

    def get_api_v1_collections_request(self):

        headers = self._headers

        response = self._http_request('get', 'collections', headers=headers)

        return response

    def get_api_v1_backups_request(self, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('get', 'backups', headers=headers, params=params)

        return response

    def get_api_v1_backups_by_id_request(self, id_, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('get', f'backups/{id_}', headers=headers, resp_type="response", params=params)

        return response

    def get_api_v1_alert_profiles_request(self, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('get', 'alert-profiles', headers=headers, params=params)

        return response

    def api_v1_version_request(self):

        headers = self._headers

        response = self._http_request('get', 'version', headers=headers)

        return response

    def get_api_v1_settings_alerts_request(self):

        headers = self._headers

        response = self._http_request('get', 'settings/alerts', headers=headers)

        return response

    def get_api_v1_settings_defender_request(self):

        headers = self._headers

        response = self._http_request('get', 'settings/defender', headers=headers)

        return response

    def get_api_v1_settings_logging_request(self, project):
        params = assign_params(project)
        headers = self._headers

        response = self._http_request('get', 'settings/logging', headers=headers, params=params)

        return response

    def api_v1_logs_console_request(self, lines):
        params = assign_params(lines=lines)

        headers = self._headers

        response = self._http_request('get', 'logs/console', params=params, headers=headers)

        return response

    def api_v1_logs_defender_request(self, hostname, lines):
        params = assign_params(hostname=hostname, lines=lines)

        headers = self._headers

        response = self._http_request('get', 'logs/defender', params=params, headers=headers)

        return response

    def delete_api_v1_users_by_id_request(self, id_):

        headers = self._headers

        response = self._http_request('delete', f'users/{id_}', headers=headers, resp_type="response")

        return response

    def delete_api_v1_groups_by_id_request(self, id_):

        headers = self._headers

        response = self._http_request('delete', f'groups/{id_}', headers=headers, resp_type="response")

        return response

    def delete_api_v1_collections_by_id_request(self, id_):

        headers = self._headers

        response = self._http_request('delete', f'collections/{id_}', headers=headers, resp_type="response")

        return response

    def delete_api_v1_alert_profiles_by_id_request(self, id_):

        headers = self._headers

        response = self._http_request('delete', f'alert-profiles/{id_}', headers=headers, resp_type="response")

        return response

    def delete_api_v1_backups_by_id_request(self, id_, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('delete', f'backups/{id_}', headers=headers, resp_type="response", params=params)

        return response

    def api_v1_backups_restore_request(self, id_, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('post', f'backups/{id_}/restore', headers=headers, resp_type="response", params=params)

        return response

    def post_api_v1_backups_request(self, name, project):
        headers = self._headers
        params = {
            "project": project
        }
        response = self._http_request('post', 'backups', headers=headers, data=f"\"{name}\"", params=params, resp_type="response")

        return response

    def patch_api_v1_backups_by_id_request(self, id_, name, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('patch', f'backups/{id_}', headers=headers, data=f"\"{name}\"", resp_type="response", params=params)

        return response

    def post_api_v1_settings_alerts_request(self, aggregationPeriodMs, consoleAddress, securityAdvisorWebhook):
        data = {
            "aggregationPeriodMs": aggregationPeriodMs,
            "consoleAddress": consoleAddress,
            "securityAdvisorWebhook": securityAdvisorWebhook
        }

        headers = self._headers

        response = self._http_request('post', 'settings/alerts', headers=headers, data=json.dumps(data), resp_type="text")

        return response

    def post_api_v1_settings_defender_request(self, settings):
        headers = self._headers

        response = self._http_request('post', 'settings/defender', headers=headers, data=json.dumps(settings), resp_type="text")

        return response

    def post_api_v1_users_request(self, config):

        headers = self._headers

        response = self._http_request('post', 'users', headers=headers, data=config, resp_type="text")

        return response

    def post_api_v1_collections_request(self, settings):

        headers = self._headers

        response = self._http_request('post', 'collections', headers=headers, data=settings, resp_type="text")

        return response

    def post_api_v1_groups_request(self, settings):

        headers = self._headers

        response = self._http_request('post', 'groups', headers=headers, data=settings, resp_type="text")

        return response

    def put_api_v1_collections_by_id_request(self, id_, settings):

        headers = self._headers

        response = self._http_request('put', f'collections/{id_}', headers=headers, data=json.dumps(settings), resp_type="text")

        return response

    def put_api_v1_users_request(self, settings):

        headers = self._headers

        response = self._http_request('put', 'users', headers=headers, data=settings, resp_type="text")

        return response


    def get_api_v1_projects_request(self):

        headers = self._headers

        response = self._http_request('get', 'projects', headers=headers)

        return response


    def get_api_v1_settings_projects_request(self, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('get', 'settings/projects', headers=headers, params=params)

        return response

    def post_api_v1_settings_projects_request(self, enabled):
        data = {
            "master": enabled
        }
        headers = self._headers

        response = self._http_request('post', 'settings/projects', headers=headers, data=json.dumps(data), resp_type="text")

        return response


    def post_api_v1_projects_request(self, settings):

        headers = self._headers

        response = self._http_request('post', 'projects', headers=headers, data=json.dumps(settings))

        return response


    def put_api_v1_projects_by_id_request(self, id_, settings):

        headers = self._headers

        response = self._http_request('put', f'projects/{id_}', headers=headers, data=settings)

        return response


    def delete_api_v1_projects_by_id_request(self, id_):

        headers = self._headers

        response = self._http_request('delete', f'projects/{id_}', headers=headers)

        return response

    def api_v1_defenders_serverless_bundle_request(self, runtime):
        params = assign_params(runtime=runtime)

        headers = self._headers

        response = self._http_request('get', 'defenders/serverless/bundle', params=params, headers=headers, resp_type="response")

        return response


    def api_v1_current_projects_request(self):

        headers = self._headers

        response = self._http_request('get', 'current/projects', headers=headers)

        return response

    def api_v1_defenders_features_request(self, id_, clusterMonitoring, proxyListenerType):

        headers = self._headers

        features = {
            "id_": id_,
            "clusterMonitoring": clusterMonitoring,
            "proxyListenerType": proxyListenerType
        }
        response = self._http_request('post', f'defenders/{id_}/features', headers=headers, data=json.dumps(features))

        return response

    def api_v1_defenders_fargatejson_request(self, data, consoleaddr, defenderType, interpreter):
        params = assign_params(consoleaddr=consoleaddr, defenderType=defenderType, interpreter=interpreter)

        headers = self._headers
        response = self._http_request('post', 'defenders/fargate.json', headers=headers,params=params, data=str(data), resp_type="response")

        return response

    def api_v1_settings_alerts_options_request(self, project):

        headers = self._headers
        params = assign_params(project=project)
        response = self._http_request('get', 'settings/alerts/options', headers=headers, params=params)

        return response

    def post_api_v1_alert_profiles_request(self, project, profile):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('post', 'alert-profiles', headers=headers, params=params, data=profile, resp_type="text")

        return response

    def get_api_v1_credentials_request(self):

        headers = self._headers

        response = self._http_request('get', 'credentials', headers=headers)

        return response

    def get_api_v1_settings_certs_request(self, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('get', 'settings/certs', headers=headers, params=params)

        return response

    def post_api_v1_credentials_request(self, data, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('post', 'credentials', headers=headers, data=data, resp_type="text", params=params)

        return response

    def post_api_v1_settings_logging_request(self, settings, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('post', 'settings/logging', headers=headers, data=settings, params=params, resp_type="text")

        return response

    def post_api_v1_settings_certs_request(self, data, project):
        params = assign_params(project=project)

        headers = self._headers

        response = self._http_request('post', 'settings/certs', headers=headers, data=data, params=params, resp_type="text")

        return response

    def get_api_v1_settings_custom_labels_request(self, project):
        params = assign_params(project=project)
        headers = self._headers

        response = self._http_request('get', 'settings/custom-labels', headers=headers, params=params)

        return response

    def post_api_v1_settings_custom_labels_request(self, labels, project):
        params = assign_params(project=project)
        headers = self._headers
        data = {
            "labels": labels
        }
        response = self._http_request('post', 'settings/custom-labels', headers=headers, params=params, data=json.dumps(data), resp_type="text")

        return response

def str_to_bool(s):
    """
    Translates string representing boolean value into boolean value
    """
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError


def format_context(context):
    """
    Format the context keys
    """
    if context and isinstance(context, dict):
        context = {pascalToSpace(key).replace(" ", ""): format_context(value) for key, value in context.items()}
    elif context and isinstance(context, list):
        context = [format_context(item) for item in context]
    return context


def translate_severity(sev):
    """
    Translates Prisma Cloud Compute alert severity into Demisto's severity score
    """

    sev = sev.capitalize()

    if sev == 'Critical':
        return 4
    elif sev == 'High':
        return 3
    elif sev == 'Important':
        return 3
    elif sev == 'Medium':
        return 2
    elif sev == 'Low':
        return 1
    return 0


def camel_case_transformer(s):
    """
    Converts a camel case string into space separated words starting with a capital letters
    E.g. input: 'camelCase' output: 'Camel Case'
    REMARK: the exceptions list below is returned uppercase, e.g. "cve" => "CVE"
    """

    transformed_string = re.sub('([a-z])([A-Z])', r'\g<1> \g<2>', str(s))
    if transformed_string in ['id', 'cve', 'arn']:
        return transformed_string.upper()
    return transformed_string.title()


def get_headers(name: str, data: list) -> list:
    """
    Returns a list of headers to the given list of objects
    If the list name is known (listed in the HEADERS_BY_NAME) it returns the list and checks for any additional headers
     in the given list
    Else returns the given headers from the given list
    Args:
        name: name of the list (e.g. vulnerabilities)
        data: list of dicts

    Returns: list of headers
    """

    # check the list for any additional headers that might have been added
    known_headers = HEADERS_BY_NAME.get(name)
    if known_headers:
        headers = known_headers[:]
    else:
        headers = []

    if isinstance(data, list):
        for d in data:
            if isinstance(d, dict):
                for key in d.keys():
                    if key not in headers:
                        headers.append(key)
    return headers


def test_module(client):
    """
    Test connection, authentication and user authorization
    Args:
        client: Requests client
    Returns:
        'ok' if test passed, error from client otherwise
    """

    client.test()
    return 'ok'


def fetch_incidents(client):
    """
    Fetches new alerts from Prisma Cloud Compute and returns them as a list of Demisto incidents
    - A markdown table will be added for alerts with a list object,
      If the alert has a list under field "tableField", another field will be added to the
      incident "tableFieldMarkdownTable" representing the markdown table
    Args:
        client: Prisma Compute client
    Returns:
        list of incidents
    """
    incidents = []
    alerts = client.list_incidents()

    if alerts:
        for a in alerts:
            alert_type = a.get('kind')
            name = ALERT_TITLE
            severity = 0

            # fix the audit category from camel case to display properly
            if alert_type == ALERT_TYPE_AUDIT:
                a['category'] = camel_case_transformer(a.get('category'))

            # always save the raw JSON data under this argument (used in scripts)
            a['rawJSONAlert'] = json.dumps(a)

            # parse any list into a markdown table, since tableToMarkdown takes the headers from the first object in
            # the list check headers manually since some entries might have omit empty fields
            tables = {}
            for key, value in a.items():
                # check only if we got a non empty list of dict
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    tables[key + 'MarkdownTable'] = tableToMarkdown(camel_case_transformer(key + ' table'),
                                                                    value,
                                                                    headers=get_headers(key, value),
                                                                    headerTransform=camel_case_transformer,
                                                                    removeNull=True)

            a.update(tables)

            if alert_type == ALERT_TYPE_VULNERABILITY:
                # E.g. "Prisma Cloud Compute Alert - imageName Vulnerabilities"
                name += a.get('imageName') + ' Vulnerabilities'
                # Set the severity to the highest vulnerability, take the first from the list
                severity = translate_severity(a.get('vulnerabilities')[0].get('severity'))

            elif alert_type == ALERT_TYPE_COMPLIANCE or alert_type == ALERT_TYPE_AUDIT:
                # E.g. "Prisma Cloud Compute Alert - Incident"
                name += camel_case_transformer(a.get('type'))
                # E.g. "Prisma Cloud Compute Alert - Image Compliance" \ "Prisma Compute Alert - Host Runtime Audit"
                if a.get('type') != "incident":
                    name += ' ' + camel_case_transformer(alert_type)

            else:
                # E.g. "Prisma Cloud Compute Alert - Cloud Discovery"
                name += camel_case_transformer(alert_type)

            incidents.append({
                'name': name,
                'occurred': a.get('time'),
                'severity': severity,
                'rawJSON': json.dumps(a)
            })

    return incidents


def api_v1_logs_defender_download_command(client, args):
    hostname = str(args.get('hostname', ''))
    lines = args.get('lines', None)

    response = client.api_v1_logs_defender_download_request(hostname, lines)

    return fileResult("logs.tar.gz", response.content)


def api_v1_list_hosts_command(client, args):
    offset = args.get('offset', None)
    limit = args.get('limit', None)
    search = str(args.get('search', ''))
    sort = str(args.get('sort', ''))
    reverse = argToBoolean(args.get('reverse', False))
    collections = str(args.get('collections', ''))
    accountIDs = str(args.get('accountIDs', ''))
    fields = str(args.get('fields', ''))
    hostname = str(args.get('hostname', ''))
    distro = str(args.get('distro', ''))
    provider = str(args.get('provider', ''))
    compact = argToBoolean(args.get('compact', False))
    clusters = str(args.get('clusters', ''))

    response = client.api_v1_hosts_request(offset, limit, search, sort, reverse, collections,
                                           accountIDs, fields, hostname, distro, provider, compact, clusters)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Host',
        outputs_key_field='Hostname',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def api_v1_containers_scan_command(client, args):

    response = client.api_v1_containers_scan_request()

    entry = {
        "Result": "Succesfully initiated scan on all containers"
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Container Scan", entry),
        raw_response=entry
    )

    return command_results


def api_v1_images_names_command(client, args):
    offset = args.get('offset', None)
    limit = args.get('limit', None)
    search = str(args.get('search', ''))
    sort = str(args.get('sort', ''))
    reverse = argToBoolean(args.get('reverse', False))
    collections = str(args.get('collections', ''))
    accountIDs = str(args.get('accountIDs', ''))
    fields = str(args.get('fields', ''))
    id_ = str(args.get('id', ''))
    hostname = str(args.get('hostname', ''))
    repository = str(args.get('repository', ''))
    registry = str(args.get('registry', ''))
    name = str(args.get('name', ''))
    layers = argToBoolean(args.get('layers', False))
    filterBaseImage = argToBoolean(args.get('filterBaseImage', False))
    compact = argToBoolean(args.get('compact', False))
    trustStatuses = str(args.get('trustStatuses', ''))
    clusters = str(args.get('clusters', ''))

    response = client.api_v1_images_names_request(offset, limit, search, sort, reverse,
                                                  collections, accountIDs,
                                                  fields, id_, hostname, repository,
                                                  registry, name, layers, filterBaseImage,
                                                  compact, trustStatuses, clusters)

    entry = {
        "Result": response
    }

    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Images',
        outputs_key_field='',
        outputs=entry,
        raw_response=entry
    )

    return command_results


def api_v1_images_command(client, args):
    offset = args.get('offset', None)
    limit = args.get('limit', None)
    search = str(args.get('search', ''))
    sort = str(args.get('sort', ''))
    reverse = argToBoolean(args.get('reverse', False))
    collections = str(args.get('collections', ''))
    accountIDs = str(args.get('accountIDs', ''))
    fields = str(args.get('fields', ''))
    id_ = str(args.get('id', ''))
    hostname = str(args.get('hostname', ''))
    repository = str(args.get('repository', ''))
    registry = str(args.get('registry', ''))
    name = str(args.get('name', ''))
    layers = argToBoolean(args.get('layers', False))
    filterBaseImage = argToBoolean(args.get('filterBaseImage', False))
    compact = argToBoolean(args.get('compact', False))
    trustStatuses = str(args.get('trustStatuses', ''))
    clusters = str(args.get('clusters', ''))

    response = client.api_v1_images_request(offset, limit, search, sort, reverse,
                                            collections, accountIDs, fields,
                                            id_, hostname, repository, registry, name,
                                            layers, filterBaseImage, compact, 
                                            trustStatuses, clusters)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Images',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def api_v1_images_download_command(client, args):
    offset = args.get('offset', None)
    limit = args.get('limit', None)
    search = str(args.get('search', ''))
    sort = str(args.get('sort', ''))
    reverse = argToBoolean(args.get('reverse', False))
    collections = str(args.get('collections', ''))
    accountIDs = str(args.get('accountIDs', ''))
    fields = str(args.get('fields', ''))
    id_ = str(args.get('id', ''))
    hostname = str(args.get('hostname', ''))
    repository = str(args.get('repository', ''))
    registry = str(args.get('registry', ''))
    name = str(args.get('name', ''))
    layers = argToBoolean(args.get('layers', False))
    filterBaseImage = argToBoolean(args.get('filterBaseImage', False))
    compact = argToBoolean(args.get('compact', False))
    trustStatuses = str(args.get('trustStatuses', ''))
    clusters = str(args.get('clusters', ''))

    response = client.api_v1_images_download_request(offset, limit, search, sort,
                                                     reverse, collections, accountIDs,
                                                     fields, id_, hostname, repository,
                                                     registry, name, layers, filterBaseImage,
                                                     compact, trustStatuses, clusters)

    return fileResult("images.csv", response.content)


def api_v1_alert_profiles_names_command(client, args):
    """
    List all alert profiles
    Args:
        None
    Returns:
        List of profiles names
    """
    response = client.api_v1_alert_profiles_names_request()
    markdown = tableToMarkdown('Profiles', response, headers="response")
    command_results = CommandResults(
        readable_output=markdown,
        outputs_prefix='PrismaCloudCompute.Profiles',
        outputs_key_field='',
        outputs=response,
        raw_response=response
    )

    return command_results


def api_v1_current_collections_command(client, args):
    """
    List all collections
    Args:
        None
    Returns:
        A list of collection objects
    """
    response = client.api_v1_current_collections_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Collections',
        outputs_key_field='Name',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def api_v1_defenders_image_name_command(client, args):
    """
    Returns the defenders image names
    Args:
        None
    Returns:
        A list of image names
    """

    response = client.api_v1_defenders_image_name_request()

    entry = {
        "Images": response
    }
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Defenders',
        outputs_key_field='Images',
        outputs=entry,
        raw_response=entry
    )

    return command_results


def api_v1_defenders_install_bundle_command(client, args):
    """
    Returns the defenders certificate bundle
    Args:
        consoleaddr: the address of the console
        defenderType: the defender type
        interpreter: custom interpreter
    Returns:
        object describing the install bundle
    """
    consoleaddr = str(args.get('consoleaddr', ''))
    defenderType = str(args.get('defenderType', ''))
    interpreter = str(args.get('interpreter', ''))
    response = client.api_v1_defenders_install_bundle_request(consoleaddr, defenderType, interpreter)
    entry = {
        "ConsoleAddress": consoleaddr,
        "Results": response
    }
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.DefenderBundles',
        outputs_key_field='ConsoleAddress',
        outputs=format_context(entry),
        raw_response=entry
    )

    return command_results


def api_v1_defenders_restart_command(client, args):
    id_ = str(args.get('id', ''))

    response = client.api_v1_defenders_restart_request(id_)
    if response.status_code == 200:
        msg = "Restart successful"
    else:
        msg = "Restart failed"

    entry = {
        "Results": msg,
        "Hostname": id_
    }

    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Restart',
        outputs_key_field='Hostname',
        outputs=entry,
        raw_response=entry
    )

    return command_results


def api_v1_defenders_names_command(client, args):
    hostname = str(args.get('hostname', ''))
    role = str(args.get('role', ''))
    cluster = str(args.get('cluster', ''))
    tasClusterIDs = str(args.get('tasClusterIDs', ''))

    response = client.api_v1_defenders_names_request(hostname, role, cluster, tasClusterIDs)
    entries = []
    for defender in response.json():
        entry = {
            "Hostname": defender
        }
        entries.append(entry)
    command_results = CommandResults(
        outputs_prefix="PrismaCloudCompute.Defenders",
        outputs_key_field="Hostname",
        outputs=entries,
        raw_response=entries
    )

    return command_results


def api_v1_defenders_summary_command(client, args):

    response = client.api_v1_defenders_summary_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.DefendersSummary',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def api_v1_deployment_host_progress_command(client, args):

    response = client.api_v1_deployment_host_progress_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.HostDeploymentProgress',
        outputs_key_field='hostname',
        outputs=response,
        raw_response=response
    )

    return command_results


def api_v1_deployment_host_scan_command(client, args):

    response = client.api_v1_deployment_host_scan_request()
    if response.status_code == 200:
        msg = "Success"
    else:
        msg = "Failure"
    entry = {
        "Status Code": response.status_code,
        "Message": msg
    }
    command_results = CommandResults(
        readable_output=tableToMarkdown("Deployment Scan", entry),
        raw_response=entry
    )

    return command_results


def api_v1_deployment_host_stop_command(client, args):

    response = client.api_v1_deployment_host_stop_request()
    if response.status_code == 200:
        msg = "Host scan stopped successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Deployment", entry),
        raw_response=entry
    )

    return command_results


def api_v1_deployment_serverless_scan_command(client, args):

    response = client.api_v1_deployment_serverless_scan_request()

    if response.status_code == 200:
        msg = "Serverless scan started successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Serverless", entry),
        raw_response=entry
    )

    return command_results


def api_v1_deployment_serverless_stop_command(client, args):

    response = client.api_v1_deployment_serverless_stop_request()
    if response.status_code == 200:
        msg = "Serverless scan stopped successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Serverless", entry),
        raw_response=entry
    )

    return command_results


def api_v1_groups_names_command(client, args):

    response = client.api_v1_groups_names_request()
    entry = {
        "PrismaCloudCompute.Groups": response
    }
    command_results = CommandResults(
        outputs=entry,
        raw_response=entry
    )

    return command_results


def get_api_v1_users_command(client, args):
    response = client.get_api_v1_users_request()

    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Users',
        outputs_key_field='Username',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_groups_command(client, args):

    response = client.get_api_v1_groups_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Groups',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_projects_command(client, args):

    response = client.get_api_v1_projects_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_collections_command(client, args):

    response = client.get_api_v1_collections_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Collections',
        outputs_key_field='Name',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_backups_command(client, args):
    project = args.get("project", None)
    response = client.get_api_v1_backups_request(project)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Backups',
        outputs_key_field='Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_backups_by_id_command(client, args):
    id_ = str(args.get('id', ''))
    project = args.get('project', None)

    response = client.get_api_v1_backups_by_id_request(id_, project)
    command_results = fileResult("backup.zip", response.content)

    return command_results


def get_api_v1_alert_profiles_command(client, args):
    project = args.get("project", None)
    response = client.get_api_v1_alert_profiles_request(project)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.AlertProfiles',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def api_v1_version_command(client, args):

    response = client.api_v1_version_request()
    entry = {"Version": response}
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Version',
        outputs=entry,
        raw_response=entry
    )

    return command_results


def get_api_v1_settings_alerts_command(client, args):

    response = client.get_api_v1_settings_alerts_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.AlertSettings',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_settings_defender_command(client, args):

    response = client.get_api_v1_settings_defender_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.DefenderSettings',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_settings_logging_command(client, args):
    project = args.get('project', None)
    response = client.get_api_v1_settings_logging_request(project)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.LoggingSettings',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def api_v1_logs_console_command(client, args):
    lines = args.get('lines', None)

    response = client.api_v1_logs_console_request(lines)
    command_results = CommandResults(
        readable_output=tableToMarkdown("Console Logs", response),
        raw_response=response
    )

    return command_results


def api_v1_logs_defender_command(client, args):
    hostname = str(args.get('hostname', ''))
    lines = args.get('lines', None)

    response = client.api_v1_logs_defender_request(hostname, lines)
    entry = {
        "Hostname": hostname,
        "Logs": response
    }
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Defenders',
        outputs=format_context(entry),
        outputs_key_field='Hostname',
        raw_response=entry,
        readable_output=tableToMarkdown("Logs", entry.get("Logs"))
    )

    return command_results


def delete_api_v1_users_by_id_command(client, args):
    id_ = str(args.get('id', ''))

    response = client.delete_api_v1_users_by_id_request(id_)
    if response.status_code == 200:
        msg = f"User {id_} deleted successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("User Deletion", entry),
        raw_response=entry
    )

    return command_results


def delete_api_v1_groups_by_id_command(client, args):
    id_ = str(args.get('id', ''))

    response = client.delete_api_v1_groups_by_id_request(id_)
    if response.status_code == 200:
        msg = f"Group {id_} deleted successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Group Deletion", entry),
        raw_response=entry
    )

    return command_results


def delete_api_v1_collections_by_id_command(client, args):
    id_ = str(args.get('id', ''))

    response = client.delete_api_v1_collections_by_id_request(id_)
    if response.status_code == 200:
        msg = f"Collection {id_} deleted successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Collection Deletion", entry),
        raw_response=entry
    )

    return command_results


def delete_api_v1_alert_profiles_by_id_command(client, args):
    id_ = str(args.get('id', ''))

    response = client.delete_api_v1_alert_profiles_by_id_request(id_)

    if response.status_code == 200:
        msg = f"Alert Profile {id_} deleted successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Alert Profile Deletion", entry),
        raw_response=entry
    )

    return command_results


def delete_api_v1_backups_by_id_command(client, args):
    id_ = str(args.get('id', ''))
    project = args.get('project', None)
    response = client.delete_api_v1_backups_by_id_request(id_, project)
    if response.status_code == 200:
        msg = f"Backup {id_} deleted successfully"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Backup Deletion", entry),
        raw_response=entry
    )

    return command_results


def api_v1_backups_restore_command(client, args):
    id_ = str(args.get('id', ''))
    project = args.get('project', None)

    response = client.api_v1_backups_restore_request(id_, project)
    if response.status_code == 200:
        msg = f"Backup {id_} restored"
    else:
        msg = "Command Failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Backup Restored", entry),
        raw_response=entry
    )

    return command_results


def post_api_v1_backups_command(client, args):
    name = str(args.get("name", ''))
    project = str(args.get("project", ''))

    response = client.post_api_v1_backups_request(name, project)
    if response.status_code == 200:
        msg = "Backup successfully created"
    else:
        msg = "Backup failed"

    entry = {
        "StatusCode": response.status_code,
        "Message": msg
    }
    command_results = CommandResults(
        readable_output=tableToMarkdown("Backup", entry),
        raw_response=entry
    )

    return command_results


def patch_api_v1_backups_by_id_command(client, args):
    id_ = str(args.get('id', ''))
    name = str(args.get('name', ''))
    project = args.get('project', None)

    response = client.patch_api_v1_backups_by_id_request(id_, name, project)
    entry = {
        "StatusCode": response.status_code,
        "Message": f"Successful rename of {id_} to {name}"
    }
    command_results = CommandResults(
        readable_output=tableToMarkdown("Backups", entry),
        raw_response=entry
    )

    return command_results


def post_api_v1_settings_alerts_command(client, args):
    aggregationPeriodMs = int(args.get("aggregationPeriodMs", None))
    consoleAddress = str(args.get("consoleAddress", ""))
    securityAdvisorWebhook = str(args.get("securityAdvisorWebhook", ""))

    response = client.post_api_v1_settings_alerts_request(aggregationPeriodMs, consoleAddress, securityAdvisorWebhook)

    entry = {
        "Status": "Alert Settings Updated",
        "aggregationPeriodMs": aggregationPeriodMs,
        "consoleAddress": consoleAddress,
        "securityAdvisorWebhook": securityAdvisorWebhook
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Alert Settings", entry),
        raw_response=entry
    )

    return command_results


def post_api_v1_settings_defender_command(client, args):
    settings = {}
    for k, v in args.items():
        if v in ["true", "True", "False", "false"]:
            settings[k] = argToBoolean(v)
        elif v.isnumeric():
            settings[k] = int(v)
        else:
            settings[k] = str(v)

    response = client.post_api_v1_settings_defender_request(settings)

    entry = {
        "Status": "Updated Defender Settings",
        "Settings": settings
    }

    command_results = CommandResults(
        readable_output=tableToMarkdown("Defender Settings", entry),
        raw_response=entry
    )

    return command_results


def post_api_v1_users_command(client, args):
    config = args.get("config")

    response = client.post_api_v1_users_request(config)
    entry = {
        "Status": "Created New User",
        "Config": config
    }
    command_results = CommandResults(
        readable_output=tableToMarkdown("User", entry),
        raw_response=entry
    )

    return command_results


def post_api_v1_collections_command(client, args):
    settings = args.get("settings")

    response = client.post_api_v1_collections_request(settings)
    entry = {
        "Status": "Success",
        "Settings": settings
    }
    command_results = CommandResults(
        readable_output=tableToMarkdown("Collection", entry),
        raw_response=entry
    )

    return command_results


def post_api_v1_groups_command(client, args):
    settings = args.get("settings")

    response = client.post_api_v1_groups_request(settings)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Groups',
        outputs_key_field='groupName',
        outputs=format_context(json.loads(settings)),
        raw_response=format_context(json.loads(settings))
    )

    return command_results


def put_api_v1_collections_by_id_command(client, args):
    id_ = str(args.get("name"))

    settings = {}

    list_arguments = [
        "hosts",
        "images",
        "labels",
        "containers",
        "functions",
        "namespaces",
        "appIDs",
        "accountIDs",
        "codeRepos",
        "clusters"
    ]
    for k, v in args.items():
        settings[k] = v.split(",") if k in list_arguments else v

    response = client.put_api_v1_collections_by_id_request(id_, settings)

    entry = {
        "Status": "Success",
        "Settings": settings
    }
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Collections',
        outputs_key_field='Name',
        outputs=format_context(settings),
        readable_output=tableToMarkdown("Collections", entry),
        raw_response=entry
    )

    return command_results


def put_api_v1_users_command(client, args):
    settings = args.get("settings")

    response = client.put_api_v1_users_request(settings)

    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Users',
        outputs_key_field='Username',
        outputs=format_context(json.loads(settings)),
        raw_response=settings
    )

    return command_results


def get_api_v1_settings_projects_command(client, args):
    project = args.get("project", "Central Console")

    response = client.get_api_v1_settings_projects_request(project)
    response["_id"] = project
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_id',
        outputs=response,
        raw_response=response
    )

    return command_results

def post_api_v1_settings_projects_command(client, args):
    enabled = argToBoolean(args.get("enabled"))

    response = client.post_api_v1_settings_projects_request(enabled)
    if enabled:
        message = "Enabled Projects"
    else:
        message = "Disabled Projects"
    
    entry = {
        "Status": "Success",
        "Message": message
    }
    command_results = CommandResults(
        readable_output=tableToMarkdown("Projects", entry),
        raw_response=response
    )

    return command_results


def post_api_v1_projects_command(client, args):
    #settings = args.get("settings")
    _id = args.get("id")
    address = args.get("address")
    ca = args.get("ca", None)
    skipVerify = argToBoolean(args.get("skipCertificateVerification", False))
    password_type = args.get("password_type", None)
    password = args.get("password", None)
    user = args.get("user", None)

    if ca:
        ca_list = ca.split(",")
    else:
        ca_list = []

    settings = {
        "_id": _id,
        "address": address,
        "ca": ca_list,
        "skipCertificateVerification": skipVerify,
        "username": user
    }
    if password and password_type == "plain":
        settings["password"] = {
            "plain": password
        }
    elif password and password_type == "encrypted":
        settings["password"] = {
            "encrypted": password
        }

    response = client.post_api_v1_projects_request(settings)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def put_api_v1_projects_by_id_command(client, args):
    #settings = args.get("settings")
    _id = args.get("id")
    address = args.get("address")
    ca = args.get("ca", None)
    skipVerify = argToBoolean(args.get("skipCertificateVerification", False))
    password_type = args.get("password_type", None)
    password = args.get("password", None)
    user = args.get("user", None)

    if ca:
        ca_list = ca.split(",")
    else:
        ca_list = []

    settings = {
        "_id": _id,
        "address": address,
        "ca": ca_list,
        "skipCertificateVerification": skipVerify,
        "username": user
    }
    if password and password_type == "plain":
        settings["password"] = {
            "plain": password
        }
    elif password and password_type == "encrypted":
        settings["password"] = {
            "encrypted": password
        }


    response = client.put_api_v1_projects_by_id_request(_id, settings)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=format_context(json.loads(settings)),
        raw_response=response
    )

    return command_results


def delete_api_v1_projects_by_id_command(client, args):
    id_ = str(args.get('id', ''))

    response = client.delete_api_v1_projects_by_id_request(id_)
    command_results = CommandResults(
        readable_output=tableToMarkdown("Projects", response),
        raw_response=response
    )

    return command_results

def api_v1_defenders_serverless_bundle_command(client, args):
    runtime = str(args.get('runtime', ''))

    response = client.api_v1_defenders_serverless_bundle_request(runtime)
    command_results = fileResult("serverless.zip", response.content)

    return command_results

def api_v1_current_projects_command(client, args):

    response = client.api_v1_current_projects_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results

def api_v1_defenders_features_command(client, args):
    id_ = str(args.get('id', ''))
    clusterMonitoring = argToBoolean(args.get('clusterMonitoring', True))
    proxyListenerType = args.get('proxyListenerType', 'default').split(',')

    response = client.api_v1_defenders_features_request(id_, clusterMonitoring, proxyListenerType)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Defenders',
        outputs_key_field='_id',
        outputs=response,
        raw_response=response
    )

    return command_results

def api_v1_defenders_fargatejson_command(client, args):
    consoleaddr = str(args.get('consoleaddr', ''))
    defenderType = str(args.get('defenderType', ''))
    interpreter = str(args.get('interpreter', ''))
    entryID = str(args.get('entryID'))
    res = demisto.getFilePath(entryID)
    file_path = res[0]['Contents']['path']

    with open(file_path, 'r') as f:
        data = f.read()

    response = client.api_v1_defenders_fargatejson_request(data, consoleaddr, defenderType, interpreter)
    command_results = fileResult("protected.json", response.content)

    return command_results

def api_v1_settings_alerts_options_command(client, args):
    project = args.get("project", None)
    
    response = client.api_v1_settings_alerts_options_request(project)
    entry = {
        "_Id": project,
        "AlertSettings": response
    }
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=format_context(entry),
        readable_output=tableToMarkdown(f"Alert Settings {entry['_Id']}", entry["AlertSettings"]),
        raw_response=response
    )

    return command_results

def post_api_v1_alert_profiles_command(client, args):
    project = args.get("project", None)
    profile = args.get("profile")

    response = client.post_api_v1_alert_profiles_request(project, profile)

    if not project:
        project = "Central Console"
    entry = format_context(json.loads(profile))
    command_results = CommandResults(
        readable_output=tableToMarkdown(f"Alert Profile {project}", entry),
        raw_response=format_context(entry)
    )

    return command_results

def get_api_v1_credentials_command(client, args):
    response = client.get_api_v1_credentials_request()
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Credentials',
        outputs_key_field='_Id',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results


def get_api_v1_settings_certs_command(client, args):
    project = args.get('project', None)
    response = client.get_api_v1_settings_certs_request(project)
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Certs',
        outputs_key_field='',
        outputs=format_context(response),
        raw_response=response
    )

    return command_results

def post_api_v1_credentials_command(client, args):
    data = args.get("data")
    project = args.get("project", None)

    response = client.post_api_v1_credentials_request(data, project)
    entry = {
        "Data": format_context(data)
    }
    if project:
        entry["_Id"] = project
    else:
        entry["_Id"] = "Central Console"
    command_results = CommandResults(
        readable_outputs=tableToMarkdown("Credentials", entry),
        raw_response=entry
    )

    return command_results

def post_api_v1_settings_logging_command(client, args):
    settings = args.get("settings")
    project = args.get("project", None)

    response = client.post_api_v1_settings_logging_request(settings, project)
    entry = {
        "LogSettings": format_context(json.loads(settings))
    }

    if project:
        entry["_Id"] = project
    else:
        entry["_Id"] = "Central Console"

    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=entry,
        readable_output=tableToMarkdown("Log Settings", entry["LogSettings"]),
        raw_response=entry
    )

    return command_results

def post_api_v1_settings_certs_command(client, args):
    data = args.get("data")
    project = args.get("project", None)
    response = client.post_api_v1_settings_certs_request(data, project)
    entry = {
        "Cert": format_context(data)
    }

    if project:
        entry["_Id"] = project
    else:
        entry["_Id"] = "Central Console"

    command_results = CommandResults(
        readable_output=tableToMarkdown("Cert Settings", entry),
        raw_response=entry
    )

    return command_results

def get_api_v1_settings_custom_labels_command(client, args):
    project = args.get("project", None)

    response = client.get_api_v1_settings_custom_labels_request(project)
    entry = {
        "Labels": response
    }

    if project:
        entry["_Id"] = project
    else:
        entry["_Id"] = "Central Console"

    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Projects',
        outputs_key_field='_Id',
        outputs=entry,
        raw_response=entry
    )

    return command_results

def post_api_v1_settings_custom_labels_command(client, args):
    project = args.get("project", None)
    labels = args.get("labels").split(",")

    response = client.post_api_v1_settings_custom_labels_request(labels, project)
    entry = {
        "Labels": labels
    }

    if project:
        entry["_Id"] = project
    else:
        entry["_Id"] = "Central Console"
    command_results = CommandResults(
        outputs_prefix='PrismaCloudCompute.Labels',
        outputs_key_field='_Id',
        outputs=entry,
        raw_response=entry
    )

    return command_results

def main():
    """
        PARSE AND VALIDATE INTEGRATION PARAMS
    """
    params = demisto.params()
    args = demisto.args()
    username = params.get('credentials').get('identifier')
    password = params.get('credentials').get('password')
    base_url = params.get('address')
    project = params.get('project', '')
    verify_certificate = not params.get('insecure', False)
    cert = params.get('certificate')
    proxy = params.get('proxy', False)

    command = demisto.command()
    # If checked to verify and given a certificate, save the certificate as a temp file
    # and set the path to the requests client
    if verify_certificate and cert:
        tmp = tempfile.NamedTemporaryFile(delete=False, mode='w')
        tmp.write(cert)
        tmp.close()
        verify = tmp.name
    else:
        # Save boolean as a string
        verify = str(verify_certificate)

    try:
        LOG(f'Command being called is {demisto.command()}')
        headers = {
            "Content-Type": "application/json"
        }

        # Init the client
        client = Client(
            base_url=urljoin(base_url, 'api/v1/'),
            verify=verify,
            auth=(username, password),
            proxy=proxy,
            project=project,
            headers=headers)

        commands = {
            "prismacloudcompute-logs-defender-download": api_v1_logs_defender_download_command,
            "prismacloudcompute-list-hosts": api_v1_list_hosts_command,
            "prismacloudcompute-containers-scan": api_v1_containers_scan_command,
            "prismacloudcompute-images-names": api_v1_images_names_command,
            "prismacloudcompute-images": api_v1_images_command,
            "prismacloudcompute-images-download": api_v1_images_download_command,
            "prismacloudcompute-alert-profiles-names": api_v1_alert_profiles_names_command,
            "prismacloudcompute-current-collections": api_v1_current_collections_command,
            "prismacloudcompute-defenders-image-name": api_v1_defenders_image_name_command,
            "prismacloudcompute-defenders-install-bundle": api_v1_defenders_install_bundle_command,
            "prismacloudcompute-defenders-restart": api_v1_defenders_restart_command,
            "prismacloudcompute-defenders-names": api_v1_defenders_names_command,
            "prismacloudcompute-defenders-summary": api_v1_defenders_summary_command,
            "prismacloudcompute-deployment-host-progress": api_v1_deployment_host_progress_command,
            "prismacloudcompute-deployment-host-scan": api_v1_deployment_host_scan_command,
            "prismacloudcompute-deployment-host-stop": api_v1_deployment_host_stop_command,
            "prismacloudcompute-deployment-serverless-scan": api_v1_deployment_serverless_scan_command,
            "prismacloudcompute-deployment-serverless-stop": api_v1_deployment_serverless_stop_command,
            "prismacloudcompute-groups-names": api_v1_groups_names_command,
            "prismacloudcompute-get-users": get_api_v1_users_command,
            "prismacloudcompute-get-groups": get_api_v1_groups_command,
            "prismacloudcompute-get-projects": get_api_v1_projects_command,
            "prismacloudcompute-get-collections": get_api_v1_collections_command,
            "prismacloudcompute-get-backups": get_api_v1_backups_command,
            "prismacloudcompute-get-backups-by-id": get_api_v1_backups_by_id_command,
            "prismacloudcompute-get-alert-profiles": get_api_v1_alert_profiles_command,
            "prismacloudcompute-version": api_v1_version_command,
            "prismacloudcompute-get-settings-alerts": get_api_v1_settings_alerts_command,
            "prismacloudcompute-get-settings-defender": get_api_v1_settings_defender_command,
            "prismacloudcompute-get-settings-logging": get_api_v1_settings_logging_command,
            "prismacloudcompute-logs-console": api_v1_logs_console_command,
            "prismacloudcompute-logs-defender": api_v1_logs_defender_command,
            "prismacloudcompute-delete-users-by-id": delete_api_v1_users_by_id_command,
            "prismacloudcompute-delete-groups-by-id": delete_api_v1_groups_by_id_command,
            "prismacloudcompute-delete-collections-by-id": delete_api_v1_collections_by_id_command,
            "prismacloudcompute-delete-alert-profiles-by-id": delete_api_v1_alert_profiles_by_id_command,
            "prismacloudcompute-delete-backups-by-id": delete_api_v1_backups_by_id_command,
            "prismacloudcompute-backups-restore": api_v1_backups_restore_command,
            "prismacloudcompute-post-backups": post_api_v1_backups_command,
            "prismacloudcompute-patch-backups-by-id": patch_api_v1_backups_by_id_command,
            "prismacloudcompute-post-settings-alerts": post_api_v1_settings_alerts_command,
            "prismacloudcompute-post-settings-defender": post_api_v1_settings_defender_command,
            "prismacloudcompute-post-users": post_api_v1_users_command,
            "prismacloudcompute-post-collections": post_api_v1_collections_command,
            "prismacloudcompute-post-groups": post_api_v1_groups_command,
            "prismacloudcompute-put-collections-by-id": put_api_v1_collections_by_id_command,
            "prismacloudcompute-put-users": put_api_v1_users_command,
            "prismacloudcompute-get-settings-projects": get_api_v1_settings_projects_command,
            "prismacloudcompute-post-settings-projects": post_api_v1_settings_projects_command,
            "prismacloudcompute-post-projects": post_api_v1_projects_command,
            "prismacloudcompute-put-projects-by-id": put_api_v1_projects_by_id_command,
            "prismacloudcompute-delete-projects-by-id": delete_api_v1_projects_by_id_command,
            "prismacloudcompute-defenders-serverless-bundle": api_v1_defenders_serverless_bundle_command,
            "prismacloudcompute-current-projects": api_v1_current_projects_command,
            "prismacloudcompute-defenders-features": api_v1_defenders_features_command,
            "prismacloudcompute-defenders-fargatejson": api_v1_defenders_fargatejson_command,
            "prismacloudcompute-settings-alerts-options": api_v1_settings_alerts_options_command,
            "prismacloudcompute-post-alert-profiles": post_api_v1_alert_profiles_command,
            "prismacloudcompute-get-credentials": get_api_v1_credentials_command,
            "prismacloudcompute-get-settings-certs": get_api_v1_settings_certs_command,
            "prismacloudcompute-post-credentials": post_api_v1_credentials_command,
            "prismacloudcompute-post-settings-logging": post_api_v1_settings_logging_command,
            "prismacloudcompute-post-settings-certs": post_api_v1_settings_certs_command,
            "prismacloudcompute-get-settings-custom-labels": get_api_v1_settings_custom_labels_command,
            "prismacloudcompute-post-settings-custom-labels": post_api_v1_settings_custom_labels_command
        }

        if demisto.command() == 'test-module':
            # This is the call made when pressing the integration test button
            result = test_module(client)
            demisto.results(result)

        elif demisto.command() == 'fetch-incidents':
            # Fetch incidents from Prisma Cloud Compute
            # this method is called periodically when 'fetch incidents' is checked
            incidents = fetch_incidents(client)
            demisto.incidents(incidents)
        else:
            return_results(commands[command](client, args))
    # Log exceptions
    except Exception as e:
        return_error(f'Failed to execute {demisto.command()} command. Error: {str(e)}')


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
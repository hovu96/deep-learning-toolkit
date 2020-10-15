from urllib.parse import parse_qs

from dltk.core.rest import BaseRestHandler
from dltk.core import connector
from dltk.core import runtime
from . import environment_api
from dltk.core import is_truthy

__all__ = [
    "EnvironmentsHandler",
    "EnvironmentParamsHandler",
]


class EnvironmentsHandler(BaseRestHandler):
    def handle_GET(self):
        results = []
        for environment in environment_api.get_all(self.splunk):
            result = {
                "name": environment.name,
                "connector": environment.connector_name,
            }
            results.append(result)
        self.send_entries(results)

    def handle_POST(self):
        params = parse_qs(self.request['payload'])
        if "name" not in params:
            raise Exception("missing name")
        runtime_name = params["name"][0]
        if "connector" not in params:
            raise Exception("missing connector")
        connector_name = params["connector"][0]
        environment_api.create(
            self.splunk,
            runtime_name,
            connector_name
        )

    def handle_DELETE(self):
        query = self.request['query']
        runtime_name = query.get("name", "")
        if not runtime_name:
            raise Exception("missing name")
        environment_api.delete(self.splunk, runtime_name)


class EnvironmentParamsHandler(BaseRestHandler):
    def handle_GET(self):
        environment_name = self.get_param("environment")
        connector_name = self.get_param("connector")
        include_runtimes = is_truthy(self.get_param("include_runtimes"))
        if environment_name:
            e = environment_api.get(self.splunk, environment_name)
            c = e.connector
            get_default = c.get_param
            def get_value(name): return e.get_param(name, inherit=False)
        elif connector_name:
            c = connector.get(self.splunk, connector_name)
            get_default = c.get_param
            def get_value(_): return None
        else:
            raise Exception("requires environment or connector")
        params = []
        params.extend([{
            "name": name,
            "default": get_default(name),
            "value": get_value(name),
            "type": "text",  # "picker" "text",
            "mandatory": False,
        } for name in ["aaaa", "bbbb"]])  # TODO: c.environment_params
        if include_runtimes:
            for r in runtime.get_all(self.splunk):  # TODO: filter by c.name
                params.extend([{
                    "runtime": r.name,
                    "name": name,
                    "default": r.get_param(name),
                    "value": "",
                    "type": "text",  # "picker" "text",
                    "mandatory": False,
                } for name in ["cccc", "dddd"]])  # TODO: c.runtime_param_names
        self.send_entries(params)
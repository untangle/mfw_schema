#!/usr/bin/python3

import argparse
import os
import unittest

import v1.databases.validate_databases_schema as validate_databases
import v1.webroot.validate_webroot_schema as webroot_system_schema
from v1.accounts import validate_accounts
from v1.alerts import validate_alerts
from v1.application_control import validate_application_control
from v1.bypass import validate_bypass
from v1.captiveportal import validate_captiveportal
from v1.dashboard import validate_dashboard
from v1.denialofservice import validate_denialofservice
from v1.dhcp import validate_dhcp
from v1.discovery import validate_discovery
from v1.dns import validate_dns
from v1.dns_filter import validate_dnsfilter
from v1.dynamic_lists import validate_dynamic_lists
from v1.files import validate_files
from v1.firewall import validate_firewall
from v1.geoip import validate_geoip
from v1.ips import validate_ips
from v1.ipsec_server import validate_ipsec_server
from v1.logger import validate_logger
from v1.network import validate_network
from v1.policy_manager import validatepolicy
from v1.quota_manager import validate_quota_manager
from v1.reports import validate_reports
from v1.routes import validate_routes
from v1.stats import validate_stats
from v1.system import validate_system_schema
from v1.threatprevention import validate_threatprevention
from v1.uris import validate_uris
from v1.wan import validate_wan
from v1.webfilter import validate_webfilter

validate_dict = {
    "accounts_schema": validate_accounts,
    "application_control_schema": validate_application_control,
    "captiveportal": validate_captiveportal,
    "dashboard_schema": validate_dashboard,
    "denialofservice": validate_denialofservice,
    "dhcp_schema": validate_dhcp,
    "discovery_schema": validate_discovery,
    "dns_schema": validate_dns,
    "dynamic_lists": validate_dynamic_lists,
    "files_schema": validate_files,
    "firewall_schema": validate_firewall,
    "geoip_schema": validate_geoip,
    "ipsec_server_schema": validate_ipsec_server,
    "logger_schema": validate_logger,
    "network_schema": validate_network,
    "policy_manager": validatepolicy,
    # disabled until https://awakesecurity.atlassian.net/browse/MFW-4121 is fixed
    "reports_schema": validate_reports,
    "routes_schema": validate_routes,
    "stats_schema": validate_stats,
    "system_schema": validate_system_schema,
    "threatprevention_schema": validate_threatprevention,
    "uris_schema": validate_uris,
    "wan_schema": validate_wan,
    "webfilter_schema": validate_webfilter,
    "quota_manager": validate_quota_manager,
    "webroot_schema": webroot_system_schema,
    "databases_schema": validate_databases,
    "bypass": validate_bypass,
    "dns_filter": validate_dnsfilter,
    "alerts": validate_alerts,
    "ips": validate_ips,
}


def main() -> None:
    """
    Grabs passed arguments, and then uses that information to validate a json file against a schema. Usage:
        > validate.py schema_file json_file
    """
    parser = argparse.ArgumentParser(description=__file__ + " Usage:")
    parser.add_argument(
        "directories",
        type=str,
        nargs="?",
        default="",
        help="directories whose schema will be validated. For multiple, separate with a comma",
    )
    parser.add_argument(
        "schema_file",
        type=str,
        nargs="?",
        default="",
        help="The schema to validate against. Blank uses directory default.",
    )
    parser.add_argument(
        "json_file",
        type=str,
        nargs="?",
        default="",
        help="The json file to validate. Blank uses directory default.",
    )
    args = parser.parse_args()

    os.environ["SCHEMA_FILE"] = args.schema_file
    os.environ["JSON_FILE"] = args.json_file
    directories = (
        args.directories.split(",") if len(args.directories) > 0 else list(validate_dict.keys())
    )
    for directory in directories:
        run_test_on_module(validate_dict[directory])
    os.environ.pop("SCHEMA_FILE", None)
    os.environ.pop("JSON_FILE", None)


def run_test_on_module(module) -> None:
    print("=== START OF MODULE TEST: " + str(module) + " ===\n")
    # Sets environment variables with the passed files, runs validation, then deletes as a teardown
    suite = unittest.TestLoader().loadTestsFromModule(module)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print("=== END OF MODULE TEST: " + str(module) + " ===\n")


if __name__ == "__main__":
    main()

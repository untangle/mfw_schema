#!/usr/bin/python3

import argparse
import os
import unittest

import v1.accounts.validate_accounts as validate_accounts
import v1.application_control.validate_application_control as validate_application_control
import v1.captiveportal.validate_captiveportal as validate_captiveportal
import v1.dashboard.validate_dashboard as validate_dashboard
import v1.databases.validate_databases_schema as validate_databases
import v1.denialofservice.validate_denialofservice as validate_denialofservice
import v1.dhcp.validate_dhcp as validate_dhcp
import v1.discovery.validate_discovery as validate_discovery
import v1.dns.validate_dns as validate_dns
import v1.dynamic_lists.validate_dynamic_lists as validate_dynamic_lists
import v1.files.validate_files as validate_files
import v1.firewall.validate_firewall as validate_firewall
import v1.geoip.validate_geoip as validate_geoip
import v1.ipsec_server.validate_ipsec_server as validate_ipsec_server
import v1.logger.validate_logger as validate_logger
import v1.network.validate_network as validate_network
import v1.policy_manager.validatepolicy as validatepolicy
import v1.reports.validate_reports as validate_reports
import v1.routes.validate_routes as validate_routes
import v1.stats.validate_stats as validate_stats
import v1.system.validate_system_schema as validate_system_schema
import v1.threatprevention.validate_threatprevention as validate_threatprevention
import v1.uris.validate_uris as validate_uris
import v1.wan.validate_wan as validate_wan
import v1.webfilter.validate_webfilter as validate_webfilter
import v1.quota_manager.validate_quota_manager as validate_quota_manager
import v1.webroot.validate_webroot_schema as webroot_system_schema
import v1.bypass.validate_bypass as validate_bypass
import v1.dns_filter.validate_dnsfilter as validate_dnsfilter
import v1.alerts.validate_alerts as validate_alerts

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
    "logger_schema" : validate_logger,
    # disabled until https://awakesecurity.atlassian.net/browse/MFW-4120 is fixed
    # "network_schema": validate_network,
    "policy_manager": validatepolicy,
    # disabled until https://awakesecurity.atlassian.net/browse/MFW-4121 is fixed
    # "reports_schema": validate_reports,
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
    "alerts":validate_alerts
}

def main():
    """
    Grabs passed arguments, and then uses that information to validate a json file against a schema. Usage:
        > validate.py schema_file json_file
    """
    parser = argparse.ArgumentParser(description=__file__ + " Usage:")
    parser.add_argument("directories", type=str, nargs='?', default="", help="directories whose schema will be validated. For multiple, separate with a comma")
    parser.add_argument("schema_file", type=str, nargs='?', default="", help="The schema to validate against. Blank uses directory default.")
    parser.add_argument("json_file", type=str, nargs='?', default="", help="The json file to validate. Blank uses directory default.")
    args = parser.parse_args()

    os.environ["SCHEMA_FILE"] = args.schema_file
    os.environ["JSON_FILE"]   = args.json_file
    directories = args.directories.split(",") if len(args.directories) > 0 else list(validate_dict.keys())
    for directory in directories:
        run_test_on_module(validate_dict[directory])
    os.environ.pop("SCHEMA_FILE", None)
    os.environ.pop("JSON_FILE", None)

def run_test_on_module(module):
    print("=== START OF MODULE TEST: " + str(module) + " ===\n")
    # Sets environment variables with the passed files, runs validation, then deletes as a teardown
    suite = unittest.TestLoader().loadTestsFromModule(module)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print("=== END OF MODULE TEST: " + str(module) + " ===\n")

if __name__ == '__main__':
    main()

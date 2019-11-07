import os

from leapp import reporting
from leapp.libraries.common.config import version


COMMON_REPORT_TAGS = [reporting.Tags.SANITY]

related = [reporting.RelatedResource('file', '/etc/os-release')]


def skip_check():
    """ Check if an environment variable was used to skip this actor """
    if os.getenv('LEAPP_DEVEL_SKIP_CHECK_OS_RELEASE'):
        reporting.create_report([
            reporting.Title('Skipped OS release check'),
            reporting.Summary('Source RHEL release check skipped via LEAPP_DEVEL_SKIP_CHECK_OS_RELEASE env var.'),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Tags(COMMON_REPORT_TAGS)
        ] + related)

        return True
    return False


def check_os_version():
    """ Check the RHEL minor version and inhibit the upgrade if it does not match the supported ones """
    if not version.is_supported_version():
        supported_releases = []
        for rel in version.SUPPORTED_VERSIONS:
            for ver in version.SUPPORTED_VERSIONS[rel]:
                supported_releases.append(rel.upper() + ' ' + ver)
        reporting.create_report([
            reporting.Title('Unsupported OS'),
            reporting.Summary(
                'The supported OS releases for the upgrade process:\n'
                ' {}'.format('\n'.join(supported_releases))
            ),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Tags(COMMON_REPORT_TAGS),
            reporting.Flags([reporting.Flags.INHIBITOR])
        ] + related)

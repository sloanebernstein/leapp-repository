import os

from leapp.actors import Actor
from leapp.models import ActiveVendorList, CopyFile, TargetUserSpacePreupgradeTasks, WpToolkit
from leapp.libraries.stdlib import api, run, CalledProcessError
from leapp.tags import TargetTransactionFactsPhaseTag, IPUWorkflowTag

VENDOR_NAME = 'wp-toolkit'
SUPPORTED_VARIANTS = ['cpanel',]

# XXX Is src_path the best place to create this file?
src_path = '/etc/leapp/files/vendors.d/wp-toolkit.var'
dst_path = '/etc/dnf/vars/wptkversion'

class SetWpToolkitYumVariable(Actor):
    """
    Records the current WP Toolkit version into a DNF variable file so that the
    precise version requested is reinstalled, and forwards the request to copy
    this data into the upgrading environment using a
    :class:`TargetUserSpacePreupgradeTasks`.
    """

    name = 'set_wp_toolkit_yum_variable'
    consumes = (ActiveVendorList, WpToolkit)
    produces = (TargetUserSpacePreupgradeTasks,)
    tags = (TargetTransactionFactsPhaseTag.Before, IPUWorkflowTag)

    def _do_cpanel(self, version):

        files_to_copy = []
        try:
            with open(src_path, 'w') as var_file:
                var_file.write(version)

            files_to_copy.append(CopyFile(src=src_path, dst=dst_path))
            api.current_logger().debug('Requesting leapp to copy {} into the upgrade environment as {}'.format(src_path, dst_path))

        except OSError as e:
            api.current_logger().error('Cannot write to {}: {}'.format(e.filename, e.strerror))

        return TargetUserSpacePreupgradeTasks(copy_files=files_to_copy)

    def process(self):

        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        if VENDOR_NAME in active_vendors:
            wptk_data = api.consume(WpToolkit)

            preupgrade_task = None
            match wptk_data.variant:
                case 'cpanel':
                    preupgrade_task = self._do_cpanel(wptk_data.version)
                case _:
                    api.current_logger().warn('Could not recognize a supported environment for WP Toolkit.')
                    return

            api.produce(preupgrade_task)

        else:
            api.current_logger().info('{} not an active vendor: skipping actor'.format(VENDOR_NAME))

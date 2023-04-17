import os

from leapp.actors import Actor
from leapp.models import ActiveVendorList, CopyFile, TargetUserSpacePreupgradeTasks
from leapp.libraries.stdlib import api, run, CalledProcessError
from leapp.tags import FactsPhaseTag, IPUWorkflowTag

VENDOR_NAME = 'wp-toolkit-cpanel'

src_path = '/etc/leapp/files/vendors.d/wp-toolkit-cpanel.var'
dst_path = '/etc/dnf/vars/wptkversion'

class SetWpToolkitYumVariable(Actor):
    """
    Records the current WP Toolkit version into a DNF variable file so that the
    precise version requested is reinstalled, and forwards the request to copy
    this data into the upgrading environment using a
    :class:`TargetUserSpacePreupgradeTasks`.
    """

    name = 'set_wp_toolkit_yum_variable'
    consumes = (ActiveVendorList,)
    produces = (TargetUserSpacePreupgradeTasks,)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    def process(self):

        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        if VENDOR_NAME in active_vendors:

            results = None
            wptk_version = ''
            try:
                results = run([ '/usr/bin/rpm', '-q', '--queryformat=%{VERSION}', 'wp-toolkit-cpanel' ])
                wptk_version = results['stdout']
                api.current_logger().info('Detected WPTK version: {}'.format(wptk_version))
            except CalledProcessError as e:
                api.current_logger().warn('Could not find the version of WP Toolkit in the RPM database.')
                return

            try:
                with open(src_path, 'w') as var_file:
                    var_file.write(wptk_version)
            except OSError as e:
                api.current_logger().error('Cannot write to {}: {}'.format(e.filename, e.strerror))
                return


            files_to_copy = []
            if os.path.isfile(src_path):
                files_to_copy.append(CopyFile(src=src_path, dst=dst_path))
                api.current_logger().debug('Requesting leapp to copy {} into the upgrade environment as {}'.format(src_path, dst_path))

            preupgrade_task = TargetUserSpacePreupgradeTasks(copy_files=files_to_copy)
            api.produce(preupgrade_task)

        else:
            api.current_logger().info('{} not an active vendor: skipping actor'.format(VENDOR_NAME))

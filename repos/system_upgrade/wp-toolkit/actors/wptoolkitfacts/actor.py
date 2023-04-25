from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.models import ActiveVendorList, InstalledRPM, WpToolkit
from leapp.tags import IPUWorkflowTag, FactsPhaseTag
from leapp.libraries.common.rpms import package_data_for

VENDOR_NAME = 'wp-toolkit'
SUPPORTED_VARIANTS = ['cpanel', ]


class WpToolkitFacts(Actor):
    """
    Go on a fact finding mission deep in the jungles of RPM for the hidden temples of wp-toolkit.
    Responsible for setting the 'variant' and 'version' variables in the WpToolkit model.
    """

    name = 'wp_toolkit_facts'
    consumes = (ActiveVendorList, InstalledRPM,)
    produces = (WpToolkit,)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):

        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            api.current_logger().info('vendor_list.data: {}'.format(vendor_list.data))
            active_vendors.extend(vendor_list.data)

        if VENDOR_NAME in active_vendors:
            api.current_logger().info('Vendor {} is active. Looking for information...'.format(VENDOR_NAME))

            version = None
            for variant in SUPPORTED_VARIANTS:
                pkgData = package_data_for(InstalledRPM, 'wp-toolkit-{}'.format(variant))
                api.current_logger().info('pkgData: {}'.format(pkgData))
                # name, arch, version, release
                if pkgData:
                    version = pkgData[2]
                    break

            if version is None:
                variant = None
                api.current_logger().warn('No WP Toolkit package appears to be installed.')
            else:
                api.current_logger().info('Found WP Toolkit variant {}, version {}'.format(variant, version))

            api.produce(WpToolkit(variant=variant, version=version))

        else:
            api.current_logger().info('{} not an active vendor: skipping actor'.format(VENDOR_NAME))

from leapp.actors import Actor
from leapp.libraries.stdlib import api, run
from leapp.models import ActiveVendorList, WpToolkit
from leapp.tags import IPUWorkflowTag, FactsPhaseTag

VENDOR_NAME = 'wp-toolkit'
SUPPORTED_VARIANTS = ['cpanel',]

class WpToolkitFacts(Actor):
    """
    No documentation has been provided for the wp_toolkit_facts actor.
    """

    name = 'wp_toolkit_facts'
    consumes = (ActiveVendorList,)
    produces = (WpToolkit,)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):

        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        if VENDOR_NAME in active_vendors:
            api.current_logger().info('Vendor {} is active. Looking for information...'.format(VENDOR_NAME))

            version = None
            for variant in SUPPORTED_VARIANTS:
                try:
                    result = run(['/usr/bin/rpm', '-q', '--queryformat=%{VERSION}', 'wp-toolkit-{}'.format(variant)])
                    version = result['stdout']
                    break
                except:
                    api.current_logger().debug('Did not find WP Toolkit variant {}'.format(variant))

            if version is None:
                variant = None
                api.current_logger().warn('No WP Toolkit package appears to be installed.')
            else:
                api.current_logger().info('Found WP Toolkit variant {}, version {}'.format(variant, version))

            api.produce(WpToolkit(variant=variant, version=version))

        else:
            api.current_logger().info('{} not an active vendor: skipping actor'.format(VENDOR_NAME))

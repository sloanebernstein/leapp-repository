from leapp.models import Model, fields
from leapp.topics import SystemFactsTopic


class WpToolkit(Model):
    topic = SystemFactsTopic

    variant = fields.String()
    version = fields.String()

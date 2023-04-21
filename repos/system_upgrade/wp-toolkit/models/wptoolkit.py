from leapp.models import Model, fields
from leapp.topics import SystemFactsTopic


class WpToolkit(Model):
    topic = SystemFactsTopic

    variant = fields.Nullable(fields.String())
    version = fields.Nullable(fields.String())

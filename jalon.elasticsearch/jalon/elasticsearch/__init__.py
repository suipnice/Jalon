from zope.i18nmessageid import MessageFactory

contentMessageFactory = MessageFactory('jalon.elasticsearch')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

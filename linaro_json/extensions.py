"""
Date-time extension, allows to serialize and deserialize datetime
objects in a consistent way. Implements equivalent of schema:

{
    "type": "string",
    "format": "date-time"
}


"""

from datetime import datetime


class datetime_extension(object):
    """
    Proxy class for serializing datetime.datetime objects.

    The serialization is a JSON string. Date is encoded
    using the ISO 8601 format:
        YYYY-MM-DDThh:mm:ssZ

    That is:
        * Four digit year code
        * Dash
        * Two digit month code
        * Dash
        * Two digit day code
        * Capital letter 'T' - time stamp indicator
        * Two digit hour code
        * Colon
        * Two digit minute code
        * Colon
        * Two digit seconds code
        * Capital letter 'Z' - Zulu (UTC) time zone indicator
    """

    FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def to_json(self, obj):
        return obj.strftime(self.FORMAT)

    @classmethod
    def from_json(self, doc):
        return datetime.strptime(doc, self.FORMAT)

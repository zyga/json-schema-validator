"""
Date-time extension, allows to serialize and deserialize datetime
objects in a consistent way. Implements equivalent of schema:

{
    "type": "string",
    "format": "date-time"
}


"""

from datetime import datetime, timedelta
import re


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
    def to_json(cls, obj):
        return obj.strftime(cls.FORMAT)

    @classmethod
    def from_json(cls, doc):
        return datetime.strptime(doc, cls.FORMAT)


class timedelta_extension(object):
    """
    Proxy for serializing datetime.timedelta instances
    """
    PATTERN = re.compile("^(\d+)d (\d+)s (\d+)us$")

    @classmethod
    def to_json(cls, obj):
        """
        Serialize wrapped datetime.timedelta instance to a string the
        with the following format:
            [DAYS]d [SECONDS]s [MICROSECONDS]us
        """
        return "{0}d {1}s {2}us".format(
                obj.days, obj.seconds, obj.microseconds)

    @classmethod
    def from_json(cls, doc):
        """
        Deserialize JSON document (string) to datetime.timedelta instance
        """
        if not isinstance(doc, basestring):
            raise TypeError("JSON document must be a string")
        match = cls.PATTERN.match(doc)
        if not match:
            raise ValueError("JSON document must match expected pattern")
        days, seconds, microseconds = map(int, match.groups())
        return timedelta(days, seconds, microseconds)

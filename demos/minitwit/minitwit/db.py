import trafaret as t
from trafaret.contrib.object_id import MongoId
from trafaret.contrib.rfc_3339 import DateTime


__all__ = ['user_schema', 'follower_schema', 'message_schema']


user_schema = t.Dict({
    t.Key("_id"): MongoId,
    t.Key("username"): t.String,
    t.Key("email"): t.String,
    t.Key("pw_hash"): t.String,
})


follower_schema = t.Dict({
    t.Key("_id"): MongoId,
    t.Key("who_id"): MongoId,
    t.Key("whom_id"): MongoId,
})


message_schema = t.Dict({
    t.Key('_id'): MongoId(allow_blank=True),
    t.Key('author_id'): MongoId,
    t.Key('text'): t.String,
    t.Key('pub_date'): DateTime,
})

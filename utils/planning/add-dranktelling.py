# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import sys
import datetime

from kn.leden.mongo import _id
from kn.base.conf import from_settings_import
from_settings_import("DT_MIN", "DT_MAX", globals())
from kn.planning.entities import Pool, Event, Vacancy


def hm2s(hours, minutes=0):
    return (hours * 60 + minutes) * 60

begin = datetime.datetime.strptime('%s %s' % (sys.argv[1], sys.argv[2]),
                                                '%Y-%m-%d %H:%M')

e = Event({
    'name': 'Dranktelling',
    'date': datetime.datetime.combine(begin.date(), datetime.time())})
e.save()

pool = Pool.by_name('barco')

for p in [1, 2]:
    v = Vacancy({
        'name': 'Teller %d' % p,
        'event': _id(e),
        'begin': begin,
        'end': begin + datetime.timedelta(seconds=1800),
        'pool': _id(pool),
        'assignee': None})
    print v._data
    v.save()

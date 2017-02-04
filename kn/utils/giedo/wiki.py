import itertools
import logging

import pymysql

from django.conf import settings
from django.utils import six

import kn.leden.entities as Es


def generate_wiki_changes(self):
    creds = settings.WIKI_MYSQL_SECRET
    if not creds:
        logging.warning('wiki: no credentials available, skipping')
        return None
    users = dict()
    id2name = dict()
    dc = pymysql.connect(
        host=creds[0],
        user=creds[1],
        password=creds[2],
        db=creds[3],
        charset='utf-8'
    )
    try:
        with dc.cursor() as c:
            c.execute("SELECT user_id, user_name FROM user")
            todo = {'add': [], 'remove': [], 'activate': [], 'deactivate': []}

            cur, old = Es.by_name('leden').get_current_and_old_members()
            for m in itertools.chain(cur, old):
                users[str(m.name)] = m
            ausers = set([u for u in users if users[u].is_active])

            for uid, user in c.fetchall():
                user = user.lower()
                if user not in users:
                    if user == 'admin':
                        continue
                    todo['remove'].append(user)
                    logging.info("wiki: removing user %s", user)
                else:
                    id2name[uid] = user
                    del users[user]
            for name, user in six.iteritems(users):
                todo['add'].append((name, six.text_type(user.humanName),
                                    user.canonical_email))

            c.execute("""SELECT ug_user FROM user_groups
                         WHERE ug_group=%s""", 'leden')
            for uid, in c.fetchall():
                if uid not in id2name:
                    continue
                user = id2name[uid]
                if user not in ausers:
                    todo['deactivate'].append(user)
                else:
                    ausers.remove(user)

            for name in ausers:
                todo['activate'].append(name)
    finally:
        dc.close()
    return todo

# vim: et:sta:bs=2:sw=4:

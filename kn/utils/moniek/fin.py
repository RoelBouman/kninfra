import koert.gnucash.export as koertexport
import six


def get_account(moniek, name, full_name, account_type):
    gcf = moniek.gcf
    result = koertexport.get_user_balance(
        gcf.book, [
            path + ":" + full_name
            for path in gcf.meta['accounts'][account_type]])
    result['mtime'] = gcf.mtime
    return result


def get_debitors(moniek):
    gcf = moniek.gcf
    return koertexport.get_debitors(gcf.book, gcf.meta['accounts']['user'])


def check_names(moniek, names):
    gcf = moniek.gcf
    book = gcf.book

    absent_from_gnucash = {}
    absent_from_website = {}

    for t, tnames in six.iteritems(names):
        paths = gcf.meta['accounts'][t]
        found_one = False

        absent_from_gnucash[t] = set()

        for name in tnames:
            for path in paths:
                if name in book.ac_by_path(path).children:
                    found_one = True
                    break
            if not found_one:
                absent_from_gnucash[t].add(name)

        absent_from_gnucash[t] = list(absent_from_gnucash[t])

    for t, paths in six.iteritems(gcf.meta['accounts']):
        absent_from_website[t] = set()
        tnames = frozenset(names[t])

        for path in paths:
            for name in book.ac_by_path(path).children:
                if name not in tnames:
                    absent_from_website[t].add(name)

        absent_from_website[t] = list(absent_from_website[t])

    return {'gnucash': absent_from_gnucash, 'website': absent_from_website}


def get_gnucash_object(moniek, year, handle):
    """Returns a list of objects with this handle,
    which should (but does not always) contain one object."""
    gcf = moniek.gcf_by_year(year)
    if gcf is None:
        return {'type': 'error', 'message': 'no such year'}
    book = gcf.book

    return [koertexport.export(obj) for obj in book.obj_by_handle(handle)]


def get_errors(moniek, year):
    gcf = moniek.gcf_by_year(year)
    if gcf is None:
        return {'type': 'error', 'message': 'no such year'}

    return koertexport.export_checks_of_book(gcf.book)


def get_years(moniek):
    return moniek.years


# vim: et:sta:bs=2:sw=4:

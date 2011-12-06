import datetime
import logging
from google.appengine.ext.mapreduce import operation as op
from codereview.models import Account, Issue


def FixIssue(issue):
  email = issue.owner.email()
  account = Account.get_by_key_name('<%s>' % email)
  iid = issue.key().id()
  if not account:
    logging.error('Issue %d has owner %s which doesn\'t exist' % (iid, email))
    return

  i_uid = issue.owner.user_id()
  a_uid = account.user.user_id()
  if i_uid != a_uid:
    canonical_date = datetime.datetime(2011, 07, 01)
    if account.modified >= canonical_date:
      logging.info('Account win! issue %d %s %s != %s' % (
          iid, email, i_uid, a_uid))
      issue.owner = account.user
      yield op.db.Put(issue)


def DeleteUnusedAccounts(account):
  email = account.user.email()
  if Issue.all().filter('owner_email =', email).get():
    return
  if Issue.all().filter('cc =', email).get():
    return
  if Issue.all().filter('reviewers =', email).get():
    return
  logging.warn('Deleting %s' % email)
  yield op.db.Delete(account)

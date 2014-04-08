"""
A subset of functions from the census app.
Use to import test data straight from the format census data comes in.
"""
from django.db import connection, transaction


@transaction.commit_on_success
def load_census_2000(filename):
    cursor = connection.cursor()
    # count the number of columns, to determine how many columns to fill
    firstline = open(filename).readline()
    cols = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
    cols.extend(map(
        lambda c: 'col%s' % str(c+1),
        range(firstline.count(',')+1-5) # subtract 5 to account for the 5 geo header columns
    ))
    cursor.copy_from(open(filename), 'census_row', sep=',', columns=cols)


@transaction.commit_on_success
def load_census_acs(filename):
    cursor = connection.cursor()
    # count the number of columns, to determine how many columns to fill
    firstline = open(filename).readline()
    cols = ['fileid', 'filetype', 'stusab', 'chariter', 'cifsn', 'logrecno']
    cols.extend(map(lambda c: 'col%s' % str(c+1),range(firstline.count(',')+1-6)))
    cursor.copy_from(open(filename), 'census_row', sep=',', columns=cols)


@transaction.commit_on_success
def load_census_2010SF(filename):
    cursor = connection.cursor()
    # count the number of columns, to determine how many columns to fill
    firstline = open(filename).readline()
    cols = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
    cols.extend(map(lambda c: 'col%s' % str(c+1), range(firstline.count(',')+1-5)))
    cursor.copy_from(open(filename), 'census_row', sep=',', columns=cols)

Tests for jalon.pas.bdd

test setup
----------

    >>> from Testing.ZopeTestCase import user_password
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()

Plugin setup
------------

    >>> acl_users_url = "%s/acl_users" % self.portal.absolute_url()
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % ('portal_owner', user_password))
    >>> browser.open("%s/manage_main" % acl_users_url)
    >>> browser.url
    'http://nohost/plone/acl_users/manage_main'
    >>> form = browser.getForm(index=0)
    >>> select = form.getControl(name=':action')

jalon.pas.bdd should be in the list of installable plugins:

    >>> 'Bdd Helper' in select.displayOptions
    True

and we can select it:

    >>> select.getControl('Bdd Helper').click()
    >>> select.displayValue
    ['Bdd Helper']
    >>> select.value
    ['manage_addProduct/jalon.pas.bdd/manage_add_bdd_helper_form']

we add 'Bdd Helper' to acl_users:

    >>> from jalon.pas.bdd.plugin import BddHelper
    >>> myhelper = BddHelper('myplugin', 'Bdd Helper')
    >>> self.portal.acl_users['myplugin'] = myhelper

and so on. Continue your tests here

    >>> 'ALL OK'
    'ALL OK'


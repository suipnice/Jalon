from AccessControl.Permissions import manage_users
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService import registerMultiPlugin

import plugin

manage_add_sygefor_form = PageTemplateFile('browser/add_plugin',
                            globals(), __name__='manage_add_sygefor_form' )


def manage_add_sygefor_helper( dispatcher, id, title=None, REQUEST=None ):
    """Add an sygefor Helper to the PluggableAuthentication Service."""

    sp = plugin.SygeforHelper( id, title )
    dispatcher._setObject( sp.getId(), sp )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'sygeforHelper+added.'
                                      % dispatcher.absolute_url() )


def register_sygefor_plugin():
    try:
        registerMultiPlugin(plugin.SygeforHelper.meta_type)
    except RuntimeError:
        # make refresh users happy
        pass


def register_sygefor_plugin_class(context):
    context.registerClass(plugin.SygeforHelper,
                          permission = manage_users,
                          constructors = (manage_add_sygefor_form,
                                          manage_add_sygefor_helper),
                          visibility = None,
                          icon='browser/icon.gif'
                         )

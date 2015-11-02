from Products.CMFCore.interfaces import IPropertiesTool
from Products.PortalTransforms.interfaces import IPortalTransformsTool
from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool

from Products.TinyMCE.interfaces.utility import ITinyMCE
from Products.TinyMCE.mimetypes import text_tinymce_output_html
from Products.TinyMCE.transforms.html_to_tinymce_output_html import html_to_tinymce_output_html
from Products.TinyMCE.transforms.tinymce_output_html_to_html import tinymce_output_html_to_html
from types import InstanceType

from zope.component import getUtility

import transaction


# add_editor
def add_editor(site):
    """ add TinyMCE to 'my preferences' """
    portal_props = getUtility(IPropertiesTool)
    site_props = getattr(portal_props, 'site_properties', None)
    attrname = 'available_editors'
    if not site_props is None:
        editors = list(site_props.getProperty(attrname))
        if 'TinyMCE' not in editors:
            editors.append('TinyMCE')
        site_props._updateProperty(attrname, editors)


# remove_editor
def remove_editor(site):
    """ Remove TinyMCE from 'my preferences' """
    portal_props = getUtility(IPropertiesTool)
    site_props = getattr(portal_props, 'site_properties', None)
    attrname = 'available_editors'
    if not site_props is None:
        editors = list(site_props.getProperty(attrname))
        editors = [x for x in editors if x != 'TinyMCE']
        site_props._updateProperty(attrname, editors)


# register_mimetype
def register_mimetype(context, mimetype):
    """ register a mimetype with the MIMETypes registry """
    if type(mimetype) != InstanceType:
        mimetype = mimetype()
    mimetypes_registry = getUtility(IMimetypesRegistryTool)
    mimetypes_registry.register(mimetype)


# unregister_mimetype
def unregister_mimetype(context, mimetype):
    """ uregister a mimetype with the MIMETypes registry """
    if type(mimetype) != InstanceType:
        mimetype = mimetype()
    mimetypes_registry = getUtility(IMimetypesRegistryTool)
    mimetypes_registry.unregister(mimetype)


# register_transform
def register_transform(context, transform):
    """ register a transform with the portal_transforms tool"""
    transform_tool = getUtility(IPortalTransformsTool)
    transform = transform()
    transform_tool.registerTransform(transform)


# unregister_transform
def unregister_transform(context, transform):
    """ unregister a transform with the portal_transforms tool"""
    transform_tool = getUtility(IPortalTransformsTool)
    # XXX How to check if transform exists?
    if hasattr(transform_tool, transform):
        transform_tool.unregisterTransform(transform)


# register_transform_policy
def register_transform_policy(context, output_mimetype, required_transform):
    """ register a transform policy with the portal_transforms tool"""
    transform_tool = getUtility(IPortalTransformsTool)
    unregister_transform_policy(context, output_mimetype)
    transform_tool.manage_addPolicy(output_mimetype, [required_transform])


# unregister_transform_policy
def unregister_transform_policy(context, output_mimetype):
    """ unregister a transform policy with the portal_transforms tool"""
    transform_tool = getUtility(IPortalTransformsTool)
    policies = [mimetype for (mimetype, required) in transform_tool.listPolicies() if mimetype == output_mimetype]
    if policies:
        # There is a policy, remove it!
        transform_tool.manage_delPolicies([output_mimetype])


# install_mimetype_and_transforms
def install_mimetype_and_transforms(context):
    """ register text/x-tinymce-output-html mimetype and transformations for captioned images """
    register_mimetype(context, text_tinymce_output_html)
    register_transform(context, tinymce_output_html_to_html)
    register_transform(context, html_to_tinymce_output_html)
    register_transform_policy(context, "text/x-html-safe", "html_to_tinymce_output_html")


# uninstall_mimetype_and_transforms
def uninstall_mimetype_and_transforms(context):
    """ unregister text/x-tinymce-output-html mimetype and transformations for captioned images """
    unregister_transform(context, "tinymce_output_html_to_html")
    unregister_transform(context, "html_to_tinymce_output_html")
    unregister_mimetype(context, text_tinymce_output_html)
    unregister_transform_policy(context, "text/x-html-safe")


# importVarious
def importVarious(context):
    if context.readDataFile('portal-tinymce.txt') is None:
        return
    site = context.getSite()
    add_editor(site)


# unregisterUtility
def unregisterUtility(context):
    my_utility = getUtility(ITinyMCE)
    context.getSiteManager().unregisterUtility(my_utility, ITinyMCE)
    del my_utility

    transaction.commit()

from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility

from logging import getLogger
LOG = getLogger('[jalon.content.browser.search]')


class SearchView(BrowserView):
    template = ViewPageTemplateFile("./jalonploneboardsearchview.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        portal_properties = getToolByName(
            context,
            "portal_properties"
        )
        self.site_properties = portal_properties.site_properties
        plone = getMultiAdapter((self.context, self.request), name="plone")
        self.normalize = getUtility(IIDNormalizer).normalize
        self.icons = plone.icons_visible()
        portal_state = getMultiAdapter(
            (context, request),
            name="plone_portal_state"
        )
        self.portal = portal_state.portal_url() + "/"

    def crop(self, text):
        plone = getMultiAdapter((self.context, self.request), name="plone")
        return plone.cropText(
            text,
            self.site_properties.search_results_description_length,
            self.site_properties.ellipsis
        )

    def update(self):
        LOG.warn("------ update ------")
        if "q" not in self.request.form:
            self.results = []
            return

        text = self.request.form["q"]
        for char in ["(", ")"]:
            text = text.replace(char, '"%s"' % char)

        ct = getToolByName(self.context, "portal_catalog")
        locale_path = "/".join(self.context.getPhysicalPath()).strip()
        LOG.warn(locale_path)
        self.results = ct(
            object_provides="Products.Ploneboard.interfaces.IComment",
            path=locale_path,
            SearchableText=text
        )

    def info(self, brain):
        """Return display-information for a search result.
        """
        obj = brain.getObject()
        conv = obj.getConversation()
        forum = obj.getForum()
        text = obj.getText()

        return dict(
            author=brain.Creator,
            title=brain.Title,
            description=self.crop(text),
            url=brain.getURL() + "/view",
            icon=self.icons and self.portal + brain.getIcon or None,
            forum_url=forum.absolute_url(),
            forum_title=forum.title_or_id(),
            conv_url=conv.absolute_url(),
            conv_title=conv.title_or_id(),
            review_state=self.normalize(brain.review_state),
            portal_type=self.normalize(brain.portal_type),
            relevance=brain.data_record_normalized_score_
        )

    def board_url(self):
        state = getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state"
        )
        return state.view_url()

    def __call__(self):
        self.update()
        return self.template()

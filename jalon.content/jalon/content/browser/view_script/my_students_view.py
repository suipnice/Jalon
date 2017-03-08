# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[MyStudentsView]')


class MyStudentsView(BrowserView):
    """Class pour le first_page
    """

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getBreadcrumbs(self):
        return [{"title": _(u"Mes etudiants"),
                 "icon":  "fa fa-users",
                 "link":  self.context.absolute_url()}]

    def getMyStudentsView(self, user):
        user_roles = user.getRoles()
        user_roles.remove("Authenticated")
        try:
            user_roles.remove("Member")
        except:
            pass
        user_role = user_roles[0]

        access_dict = self.getAccessDict(user.getId()) if user_role == "Personnel" else {}

        my_students_macro_dict = {"Etudiant":      "my_class_mates",
                                  "EtudiantJalon": "my_class_mates",
                                  "Personnel":     "my_students",
                                  "Secretaire":    "all_students",
                                  "Manager":       "all_students"}
        return {"my_students_macro": my_students_macro_dict[user_role],
                "access_dict":       access_dict}

    def getAccessDict(self, user_id):
        LOG.info("----- getAccessDict START-----")
        portal = self.context.portal_url.getPortalObject()
        portal_catalog = portal.portal_catalog

        LOG.info("SEARCH Creator")
        course_list = list(portal_catalog.searchResults(portal_type="JalonCours", Creator=user_id))
        LOG.info(course_list)

        LOG.info("SEARCH getAuteurPrincipal")
        course_list.extend(list(portal_catalog.searchResults(portal_type="JalonCours", getAuteurPrincipal=user_id)))
        #if author_course_list:
        #    course_list.extend(author_course_list)
        LOG.info(course_list)

        LOG.info("SEARCH getCoAuteurs")
        course_list.extend(list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=user_id)))
        LOG.info(course_list)
        #coauthor_course_list = list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=user_id))
        #if coauthor_course_list:
        #    course_list.extend(coauthor_course_list)

        course_access_dict = {}
        not_access_dict = {"etape":  "Le code *-* n'est plus valide pour ce diplôme.",
                           "ue":     "Le code *-* n'est plus valide pour cette UE / UEL.",
                           "uel":    "Le code *-* n'est plus valide pour cette UE / UEL.",
                           "groupe": "Le code *-* n'est plus valide pour ce groupe."}
        portal_jalon_bdd = portal.portal_jalon_bdd
        for course in course_list:
            LOG.info("FOR COURSE : %s" % course.getId)
            for course_access in course.getListeAcces:
                LOG.info("FOR COURSE ACCESS : %s" % course_access)
                access_type, access_code = course_access.split("*-*")
                LOG.info((access_type, access_code))
                if not access_code in course_access_dict:
                    access_response_request = portal_jalon_bdd.getELPData(access_code)
                    if not access_response_request:
                        access_data = [not_access_dict[access_type].replace("*-*", access_code), access_type, access_code, access_code, "0"]
                    else:
                        access_data = list(access_response_request)
                    course_access_dict[access_code] = {"access_title":       access_data[0],
                                                       "access_code":        access_data[3] if access_data[1] == "groupe" else access_data[2],
                                                       "access_type":        access_data[1],
                                                       "access_students":    access_data[4],
                                                       "access_course_list": [course.Title]}
                else:
                    if not course.Title in course_access_dict[access_code]["access_course_list"]:
                        course_access_dict[access_code]["access_course_list"].append(course.Title)
        LOG.info("----- getAccessDict END-----")
        return course_access_dict

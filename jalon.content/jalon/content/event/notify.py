# -*- coding: utf-8 -*-
# Created relative to Products.Products.PloneboardNotify

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from jalon.content.event import html_template

try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
except ImportError:
    # py24
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText

import re

raw_url_finder = r"""<a.*?class=\"internal-link\".*?href=\"(?P<url1>.*?)\".*?</a>"""
"""|<a.*?href=\"(?P<url2>.*?)\".*?class=\"internal-link\".*?</a>"""
url_finder = re.compile(raw_url_finder)

match_start = "href=\""


def sendMail(object, event):
    conversation = object.getConversation()
    forum = conversation.getForum()
    cours = forum.aq_parent.aq_parent
    if not cours.getActiverEmailForum():
        return None

    portal = getToolByName(object, "portal_url").getPortalObject()
    portal_transforms = getToolByName(object, "portal_transforms")
    portal_membership = getToolByName(object, "portal_membership")
    jalon_bdd = getToolByName(object, "portal_jalon_bdd")

    authMember = portal_membership.getAuthenticatedMember()
    send_from = authMember.getProperty("email")
    if not send_from:
        send_from = portal.getProperty("email_from_address")

    send_to = []
    for acces in cours.getListeAcces():
        code = acces.split("*-*")[1]
        listeEtudiants = jalon_bdd.rechercherUtilisateurs(code, "Etudiant", True)
        for etudiant in listeEtudiants:
            if etudiant["EMAIL_ETU"] and not etudiant["EMAIL_ETU"] in send_to:
                if not etudiant["EMAIL_ETU"] in send_to:
                    send_to.append(etudiant["EMAIL_ETU"])
    for invitation in cours.getInvitations():
        if not invitation in send_to:
            send_to.append(invitation)
    for auteur in cours.getCoAuteursCours():
        if not auteur["email"] in send_to:
            send_to.append(auteur["email"])
    for lecteur in cours.getCourseReader():
        if not lecteur["email"]:
            send_to.append(lecteur["email"])
    if not cours.getAuteur()["email"] in send_to:
        send_to.append(cours.getAuteur()["email"])
    #object.plone_log(send_to)

    translation_service = getToolByName(object, 'translation_service')
    # I use the dummy vars below to make i18ndude works

    dummy = _(u"Nouveau message ajouté dans un forum")
    msg_sbj = u"Nouveau message ajouté dans un forum"
    subject = translation_service.utranslate(domain='jalon.content',
                                             msgid=msg_sbj,
                                             default=msg_sbj,
                                             context=object)
    subject = "[%s]" % portal.Title() + subject
    #object.plone_log(subject)

    dummy = _(u"Message ajouté par : ")
    msg_from = u"Message ajouté par : "
    from_user = translation_service.utranslate(domain='jalon.content',
                                               msgid=msg_from,
                                               default=msg_from,
                                               context=object)
    send_from_fullname = authMember.getProperty("fullname")
    if not send_from_fullname:
        send_from_fullname = authMember.getProperty("displayName")
    from_user += send_from_fullname.decode('utf-8')
    #object.plone_log(from_user)

    dummy = _(u"Nouveau message ajouté dans le forum: ")
    msg_arg_1 = u"Nouveau message ajouté dans le forum: "
    argument = translation_service.utranslate(domain='jalon.content',
                                              msgid=msg_arg_1,
                                              default=msg_arg_1,
                                              context=object)
    argument += forum.Title().decode('utf-8')
    dummy = _(u", pour le cours: ")
    msg_arg_2 = u", pour le cours: "
    argument += translation_service.utranslate(domain='jalon.content',
                                               msgid=msg_arg_2,
                                               default=msg_arg_2,
                                               context=object)
    argument += cours.Title().decode('utf-8')
    #object.plone_log(argument)

    dummy = _(u"Le nouveau message est:")
    msg_txt = u"Le nouveau message est:"
    new_mess = translation_service.utranslate(domain='jalon.content',
                                              msgid=msg_txt,
                                              default=msg_txt,
                                              context=object)
    #object.plone_log(new_mess)

    html_body = object.REQUEST.form['text'].decode('utf-8')
    html_body = html_body.replace("\n", "<br/>")
    #html_body = html_body.replace("\t", "<br/>")
    here_url = object.absolute_url()

    def fixURL(match):
        """Fix relative URL to absolute ones"""
        value = match.group()
        pos_s = value.find(match_start)+len(match_start)
        pos_e = value.find('"', pos_s+1)
        url = value[pos_s:pos_e]
        if not url.startswith(here_url):
            return value.replace(url, "%s/%s" % (here_url, url))
        return value

    html_body = url_finder.sub(fixURL, html_body)

    text = html_template.message % ({'from': from_user,
                                     'argument': argument,
                                     'message_intro': new_mess,
                                     'message': html_body,
                                     'url': here_url,
                                     'url_text': here_url,
                                     })
    #object.plone_log(text)

    text = text.encode("utf-8")
    data_to_plaintext = portal_transforms.convert("html_to_web_intelligent_plain_text", text)
    plain_text = data_to_plaintext.getData()

    for to in send_to:
        #msg = MIMEMultipart()
        msg = MIMEMultipart('alternative')
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(plain_text, 'plain', _charset="utf-8")
        part2 = MIMEText(text, 'html', _charset="utf-8")

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        msg['to'] = to
        msg['from'] = "no-reply@unice.fr"
        msg['subject'] = subject
        msg.add_header('reply-to', send_from)

        mail_host = getToolByName(object, 'MailHost')
        #object.plone_log("Message subject: %s" % subject)
        #object.plone_log("Message text:\n%s" % text)
        #object.plone_log("Message sent to %s", to)
        #object.plone_log(msg.as_string().encode("utf-8"))

        try:
            mail_host.send(msg)
        except Exception, inst:
            putils = getToolByName(object, 'plone_utils')
            putils.addPortalMessage(_(u'Not able to send notifications'))
            object.plone_log("Error sending notification: %s" % str(inst))

"""Class: SygeforHelper
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements, createViewName

from OFS.Cache import Cacheable

# Pluggable Auth Service
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, IPropertiesPlugin, IRolesPlugin, IUserEnumerationPlugin

# PlonePAS
from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin
from Products.PlonePAS.sheet import MutablePropertySheet

# SQL Alchemy
import sqlalchemy as rdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, contains_eager

import interface
import plugins
import models

import datetime
import copy

def safeencode(v):
    if isinstance(v, unicode):
        return v.encode('utf-8')
    return v

"""
def getSession():
    engine = create_engine('mysql+pymysql://login:pass@dns/base', echo=True)
    return sessionmaker(bind=engine)

Session = getSession()
"""

class SygeforHelper(BasePlugin, Cacheable):
    """Multi-plugin

    """

    meta_type = 'sygefor Helper'
    security = ClassSecurityInfo()

    serviceUrl = ""
    _properties = (
        {
            'id': 'serviceUrl',
            'lable': 'Service URL',
            'type': 'string',
            'mode': 'w'
            },)

    def __init__( self, id, title=None ):
        self._setId( id )
        self.title = title

    #
    # IAuthenticationPlugin implementation
    #

    security.declarePrivate('authenticateCredentials')
    #@graceful_recovery(log_args=False)
    def authenticateCredentials(self, credentials):
        #print "--- authenticateCredentials ---"
        login = credentials.get('login')
        password = credentials.get('password')

        if credentials.get("extractor") == "plone-session": return None

        #print "login : %s" % login
        #print "password : %s" % password
        #print credentials

        if not login or not password or login == "admin":
            return None

        #if login.startswith("0syg0"): login = login[5:] 
        session = self.Session()
        #print "session %s" % session.connection()
        print "connexion"
        user = session.query(models.User).filter_by(loginStagiaire=login).first()
        #print "user : %s" % user

        session.close()
        if user is not None and user.check_password(password):
            #print "ok"
            return (login, login)

    security.declarePrivate('enumerateUsers')
    #@graceful_recovery(())
    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):
        """See IUserEnumerationPlugin."""
        
        if id: return ({'login': id, 'pluginid': self.getId(), 'id': id},)
        else: return ({'login': login, 'pluginid': self.getId(), 'id': login},)

        #if login.startswith("0syg0"): login = login[5:]
        view_name = createViewName('enumerateUsers', id or login)

        if isinstance(id, basestring):
            id = [str(id)]
        if isinstance(login, basestring):
            login = [str(login)]

        # check cached data
        keywords = copy.deepcopy(kw)
        print "------------ enumerateUsers ------------------"
        print keywords
        print max_results
        #print "id : %s" % id
        #print "login : %s" % login
        #print "---------- enumerateUsers (fin) --------------"
        
        info = {
            'id': id,
            'login': login,
            'exact_match': exact_match,
            'sort_by': sort_by,
            'max_results': max_results,
        }
        keywords.update(info)
        cached_info = self.ZCacheable_get(
            view_name=view_name, keywords=keywords)
        if cached_info is not None:
            return cached_info

        terms = []
        if id is not None:
            terms.extend(id)
        if login is not None:
            terms.extend(login)

        session = self.Session()
        query = session.query(models.User)
        column = models.User.loginStagiaire
        clause = None

        if exact_match:
            max_results = 1
            for term in terms:
                clause = rdb.or_(clause, column.like(term))
        else:
            for term in terms:
                clause = rdb.or_(
                    clause,
                    rdb.or_(column.ilike(term), column.contains(term)))

        if exact_match and clause is None:
            users = ()
        else:
            users = query.filter(clause).all()

        all = {}
        pas = self.aq_parent
        for n, user in enumerate(users):
            user_id = user.loginStagiaire
            data = {
                'id': safeencode(user_id),
                'login': safeencode(user_id),
                'pluginid': self.getId()
            }

            if max_results is not None and len(all) == max_results:
                break

            if kw:
                # this is crude filtering, but better than none
                try:
                    user = pas.getUserById(user_id)
                    keep = True
                    for k, v in kw.items():
                        p = user.getProperty(k, None)
                        if not isinstance(v, basestring):
                            if p != v:
                                keep = False
                                break
                        else:
                            if p.lower().find(v.lower()) == -1:
                                keep = False
                                break
                    if not keep:
                        continue
                except:
                    # any problems getting a user? forget this check
                    pass

            if exact_match or not terms:
                all.setdefault(user_id, data)
            else:
                for term in terms:
                    if term in user_id:
                        all.setdefault(user_id, data)
                        if max_results is not None and len(all) == max_results:
                            break

        values = tuple(all.values())

        #print "---------------- enumerateUsers values -------------------------"
        #print id
        #print login
        print values
        print "---------------- enumerateUsers values (fin) -------------------"
        # Cache data upon success
        session.close()
        self.ZCacheable_set(values, view_name=view_name, keywords=keywords)
        return values

    #
    # IPropertiesPlugin implementation
    #
    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """Get property values for a user or group.
        Returns a dictionary of values or a PropertySheet.
        """

        #print "--- getPropertiesForUser ---"
        #print request.SESSION

        #print request.SESSION    
        if request and "__cas_assertion" in  str(request.SESSION): return None

        try:
           username = user.getUserName()
        except:
           username = user
        if request and request.SESSION.get("sheetSygefor%s" % username):
           print "session"
           return request.SESSION.get("sheetSygefor%s" % username)
        print "pas de session"

        #view_name = createViewName('getPropertiesForUser', username)
        #cached_info = self.ZCacheable_get(view_name=view_name)
        #if cached_info is not None:
        #    return MutablePropertySheet(self.id, **cached_info)
        #print "Pas en cache"
        data = None
        session = self.Session()

        login = username
        #if login.startswith("0syg0"): login = login[5:] 
        #user = session.query(models.User).join(models.UserInfos, models.User.idTiers==models.UserInfos.idTiers).filter(models.User.loginStagiaire==user.getUserName()).options(contains_eager(models.User)).first()
        userSyg = session.query(models.User).filter(models.User.loginStagiaire==login).first()
        #user = session.query(models.User.idTiers, models.UserInfos.idTiers).filter(rdb.and_(models.User.idTiers==models.UserInfos.idTiers, models.User.loginStagiaire==user.getUserName())).first()

        if userSyg is not None:
            d = userSyg.__dict__.copy()
            #print d

            # remove system attributes
            d.pop('loginStagiaire')
            d.pop('passwordStagiaire')

            # convert dates
            for name, value in d.items():
                if isinstance(value, datetime.datetime):
                    d[name] = DateTime(str(value))

            data = dict(
                (name, value)
                for (name, value) in d.items()
                if not name.startswith('_') and value is not None)
            
            user_infos = session.query(models.UserInfos).filter(models.UserInfos.idTiers==int(data["idTiers"])).first()
            if user_infos:
               dico = user_infos.__dict__.copy()
               data["fullname"] = "%s %s" % (dico["nomTiers"], dico["prenomTiers"])
               data["email"] = dico["mailTiers"]
            #data["fullname"] = "%s %s" % (data["lastname"], data["firstname"])
            #print data
        session.close()
        #self.ZCacheable_set(data, view_name=view_name)
        if data:
            #self.ZCacheable_set(data, view_name=view_name)
            idSyg = data.pop('id', None)
            sheet = MutablePropertySheet(idSyg, **data)
            if request: request.SESSION.set("sheetSygefor%s" % username, sheet)
            return sheet

    #
    # IRolesPlugin implementation
    #
    def getRolesForPrincipal(self, principal, request=None ):
        #print "--- getRolesForPrincipal ---"
        return ("Authenticated", "Sygefor")

    def Session(self):
        engine = create_engine(self.serviceUrl, echo=False)
        return sessionmaker(bind=engine)()

classImplements(SygeforHelper,
                IAuthenticationPlugin,
                IPropertiesPlugin,
                IRolesPlugin,
                IUserEnumerationPlugin,)

InitializeClass( SygeforHelper )

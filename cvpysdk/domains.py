# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""File for performing domain related operations.


Domains: Class for representing all the associated domains with the commcell.


Domains:

    __init__(commcell_object)  --  initialize instance of the Domains associated with
                                       the specified commcell

    __str__()                  --  returns all the domains associated with the commcell

    __repr__()                 --  returns the string for the instance of the Domains class

    _get_domains()             --  gets all the domains associated with the commcell specified

    has_domain()               --  checks if a domain exists with the given name or not

    get(domain_name)           --  returns the instance of the Domain class,
                                       for the the input domain name

    delete(domain_name)        --  deletes the domain from the commcell

    refresh()                  --  refresh the domains associated with the commcell


"""

from __future__ import absolute_import
from __future__ import unicode_literals

from base64 import b64encode
from past.builtins import basestring

from .exception import SDKException


class Domains(object):
    """Class for getting all the domains associated with a commcell."""

    def __init__(self, commcell_object):
        """Initialize object of the Domains class.

            Args:
                commcell_object     (object)    --  instance of the Commcell class

            Returns:
                object - instance of the Domains class

        """
        self._commcell_object = commcell_object

        self._cvpysdk_object = commcell_object._cvpysdk_object
        self._services = commcell_object._services
        self._update_response_ = commcell_object._update_response_

        self._DOMAIN_CONTROLER = self._services['DOMAIN_CONTROLER']

        self._domains = None
        self.refresh()

    def __str__(self):
        """Representation string consisting of all domains of the Commcell.

            Returns:
                str - string of all the domains for a commcell

        """
        representation_string = "{:^5}\t{:^50}\n\n".format('S. No.', 'Domain')

        for index, domain_name in enumerate(self._domains):
            sub_str = '{:^5}\t{:30}\n'.format(index + 1, domain_name)
            representation_string += sub_str

        return representation_string.strip()

    def __repr__(self):
        """Representation string for the instance of the Domains class."""
        return "Domains class instance for Commcell: '{0}'".format(
            self._commcell_object.webconsole_hostname
        )

    def _get_domains(self):
        """Gets all the domains associated with the commcell

            Returns:
                dict - consists of all domain in the commcell

                    {
                         "domain1_name": domain_Details_dict1,

                         "domain2_name": domain_Details_dict2
                    }

            Raises:
                SDKException:
                    if response is empty

                    if response is not success

        """
        flag, response = self._cvpysdk_object.make_request('GET', self._DOMAIN_CONTROLER)

        if flag:
            domains_dict = {}

            if response.json() and 'providers' in response.json():
                response_value = response.json()['providers']

                for temp in response_value:
                    temp_name = temp['shortName']['domainName'].lower()
                    temp_details = temp
                    domains_dict[temp_name] = temp_details

            return domains_dict
        else:
            response_string = self._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def has_domain(self, domain_name):
        """Checks if a domain exists in the commcell with the input domain name.

            Args:
                domain_name     (str)   --  name of the domain

            Returns:
                bool    -   boolean output whether the domain exists in the commcell or not

            Raises:
                SDKException:
                    if type of the domain name argument is not string

        """
        if not isinstance(domain_name, basestring):
            raise SDKException('Domain', '101')

        return self._domains and domain_name.lower() in self._domains

    def get(self, domain_name):
        """Returns a domain object of the specified domain name.

            Args:
                domain_name (str)  --  name of the domain

            Returns:
                dict - properties of domain.

            Raises:
                SDKException:
                    if type of the domain name argument is not string

                    if no domain exists with the given name

        """
        if not isinstance(domain_name, basestring):
            raise SDKException('Domain', '101')
        else:
            domain_name = domain_name.lower()

            if self.has_domain(domain_name):
                return self._domains[domain_name]
            else:
                raise SDKException(
                    'Domain', '102', 'No domain exists with name: {0}'.format(domain_name)
                )

    def delete(self, domain_name):
        """Deletes the domain from the commcell.

            Args:
                domain_name     (str)   --  name of the domain to remove from the commcell

            Raises:
                SDKException:
                    if type of the domain name argument is not string

                    if failed to delete domain

                    if response is empty

                    if response is not success

                    if no domain exists with the given name

        """

        if not isinstance(domain_name, basestring):
            raise SDKException('Domain', '101')
        else:
            domain_name = domain_name.lower()

            if self.has_domain(domain_name):
                domain_id = str(self._domains[domain_name]["shortName"]["id"])
                delete_domain = self._services['DELETE_DOMAIN_CONTROLER'] % (domain_id)

                flag, response = self._cvpysdk_object.make_request('DELETE', delete_domain)

                if flag:
                    if response.json() and 'errorCode' in response.json():
                        error_code = response.json()["errorCode"]

                        if error_code == 0:
                            # initialize the domain again
                            # so the domains object has all the domains
                            self.refresh()
                        else:
                            o_str = ('Failed to delete domain with error code: "{0}"'
                                     '\nPlease check the documentation for '
                                     'more details on the error')
                            raise SDKException(
                                'Domain', '102', o_str.format(error_code)
                            )
                    else:
                        raise SDKException('Response', '102')
                else:
                    response_string = self._update_response_(response.text)
                    raise SDKException('Response', '101', response_string)
            else:
                raise SDKException(
                    'Domain', '102', 'No domain exists with name: {0}'.format(domain_name)
                )

    def refresh(self):
        """Refresh the domains associated with the Commcell."""
        self._domains = self._get_domains()

    def add(self,
            domain_name,
            netbios_name,
            user_name,
            password,
            ad_proxy_list=None,
            enable_sso=True):
        """Adds a new domain to the commcell.

            Args:
                domain_name     (str)   --  name of the domain

                netbios_name    (str)   --  netbios name of the domain

                user_name       (str)   --  user name of the domain

                password        (str)   --  password of the domain

                adProxyList     (list)  --  list of client objects to be used as proxy.

                    default: None

                    if no proxy required

                enable_sso      (bool)  --  enable sso for domain

            Returns:
                dict    -   properties of domain

            Raises:
                SDKException:
                    if type of the domain name argument is not string

                    if no domain exists with the given name

        """
        if not (isinstance(domain_name, basestring) and
                isinstance(netbios_name, basestring) and
                isinstance(user_name, basestring) and
                isinstance(password, basestring)):
            raise SDKException('Domain', '101')
        else:
            domain_name = domain_name.lower()

            if self.has_domain(domain_name):
                return self._domains[domain_name]

        proxy_information = {}

        if ad_proxy_list:
            if isinstance(ad_proxy_list, list):
                proxy_information = {
                    'adProxyList': [{"clientName": client} for client in ad_proxy_list]
                }
            else:
                raise SDKException('Domain', '101')

        domain_create_request = {
            "operation": 1,
            "provider": {
                "serviceType": 2,
                "flags": 1,
                "bPassword": b64encode(password.encode()).decode(),
                "login": user_name,
                "enabled": 1,
                "useSecureLdap": 0,
                "connectName": domain_name,
                "bLogin": user_name,
                "tppm": {
                    "enable": True if ad_proxy_list else False,
                    "tppmType": 4,
                    "proxyInformation": proxy_information
                },
                "shortName": {
                    "domainName": netbios_name
                }
            }
        }

        flag, response = self._cvpysdk_object.make_request(
            'POST', self._DOMAIN_CONTROLER, domain_create_request
        )

        if flag:
            if response.json() and 'errorCode' in response.json():
                error_code = response.json()["errorCode"]

                if error_code == 0:
                    # initialize the domain again
                    # so the domains object has all the domains
                    self.refresh()
                else:
                    o_str = ('Failed to add domain with error code: "{0}"'
                             '\nPlease check the documentation for '
                             'more details on the error')
                    raise SDKException(
                        'Domain', '102', o_str.format(error_code)
                    )
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._update_response_(response.text)
            raise SDKException('Response', '101', response_string)
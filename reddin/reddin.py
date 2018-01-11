"""Xblock which render remote content by url in iframe and send crypted student data in GET param."""

import json
import urllib

import pkg_resources
from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Dict, Scope, String

from django.template import Template, Context
from django.conf import settings
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import AESCipher

# Make '_' a no-op so we can scrape strings
_ = lambda text: text

@XBlock.needs('user')
class ReddinXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Xblock which render remote content by url in iframe and send crypted student data in GET param.
    """
    display_name = String(
        display_name=_("Display Name"),
        help=_("This name appears in the horizontal navigation at the top of the page."),
        default="Reddin XBlock",
        scope=Scope.settings
    )

    url = String(
        display_name=_("Reddin URL"),
        default="",
        scope=Scope.content
    )

    data_params = Dict(
        display_name=_("URL Parameters"),
        help=_('Example: {"name1": "value1", "name2": "value2"}'),
        default={},
        scope=Scope.content
    )

    editable_fields = ('display_name', 'url', 'data_params')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the ReddinXBlock, shown to students
        when viewing courses.
        """
        encoded = self.get_encoded_data()
        parameters = ''
        if self.data_params:
            for key, value in self.data_params.items():
                parameter = '&{}={}'.format(key, value)
                parameters += parameter

        context['url_string'] = self.url + encoded + parameters if self.url else ""
        html = self.render_template("static/html/reddin.html", context)
        frag = Fragment(html.format(self=self))
        return frag

    def render_template(self, template_path, context):
        """
        Allow django template processing

        :param template_path: path to template
        :param context: context dictionary
        :return: rendered content
        """
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def is_course_staff(self):
        # pylint: disable=no-member
        """
         Check if user is course staff.
        """
        return getattr(self.xmodule_runtime, 'user_is_staff', False)

    def get_encoded_data(self):
        """
        Collect all data needed and encode it
        Returns: string

        """
        user = self.runtime.service(self, "user")._django_user
        data = {
            'course_id': str(self.course_id),
            'username': user.username,
            'email': user.email,
            'fullname': "%s %s" % (user.first_name, user.last_name)

        }
        row = json.dumps(data)
        encoded = AESCipher(settings.FEATURES['REDDIT_SECRET_KEY']).encrypt(row)
        return "?data=" + urllib.quote(encoded)

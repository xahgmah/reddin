"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import HTMLParser
import urllib
from xblock.core import XBlock
from xblock.fields import Scope, Integer
from xblock.fragment import Fragment
from xblock.fields import Scope, String, Dict, Float

from submissions.models import StudentItem as SubmissionsStudent, Submission
from django.template import Template, Context
from Crypto.Cipher import AES
from student.models import user_by_anonymous_id
from .utils import AESCipher
import json
import base64

html_parser = HTMLParser.HTMLParser()


class ReddinXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    url = String(help="Reddin URL", default="", scope=Scope.content)
    display_name = String(
        help="This name appears in the horizontal navigation at the top of"
             "the page.",
        default="",
        scope=Scope.settings
    )
    weight = Float(
        display_name="Problem Weight",
        help=("Defines the number of points each problem is worth. "
              "If the value is not set, the problem is worth the sum of the "
              "option point values."),
        values={"min": 0, "step": .1},
        scope=Scope.user_state
    )

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )

    REDDIT_SECRET_KEY = "1234567890123456"

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the ReddinXBlock, shown to students
        when viewing courses.
        """
        encoded = self.get_encoded_data()
        context['url_string'] = self.url + encoded
        html = self.render_template("static/html/reddin.html", context)
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/reddin.css"))
        frag.add_javascript(self.resource_string("static/js/src/reddin.js"))
        frag.initialize_js('ReddinXBlock')
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
        return html_parser.unescape(template.render(Context(context)))

    def studio_view(self, context=None):
        """
        The primary view of the ReddinXBlock, shown to instructor
        when editing in studio.
        """
        html = self.resource_string("static/html/studio.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        frag.initialize_js('ReddinXBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.display_name = data.get('display_name')
        if self.url != data.get('url'):
            # remove all submissions if url was changed for the same block
            qs = Submission.objects.select_related('student_item').filter(
                student_item__course_id=self.course_id,
                student_item__item_id=self.scope_ids.usage_id,
                student_item__item_type='reddin'
            ).delete()
        self.url = data.get('url')

        return {'result': 'success'}

    def get_encoded_data(self, ):
        """
        Collect all data needed and encode it
        Returns: string

        """
        user = user_by_anonymous_id(self.runtime.anonymous_student_id)
        data = {
            'course_id': str(self.course_id),
            'username': user.username,
            'email': user.email

        }
        row = json.dumps(data)
        ac = AESCipher(self.REDDIT_SECRET_KEY)
        encoded = ac.encrypt(row)
        return "?data=" + encoded

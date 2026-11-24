import jinja2 as _jinja2
import markupsafe as _markupsafe

_jinja2.Markup = _markupsafe.Markup
_jinja2.escape = _markupsafe.escape
_jinja2.contextfilter = _jinja2.pass_context
_jinja2.environmentfilter = _jinja2.pass_environment

from jinja2 import Environment, Markup, contextfilter, environmentfilter, escape


@environmentfilter
def money(env, value):
    return f"{env.globals['currency']}{value:,.2f}"


@contextfilter
def greet(context, name):
    return f"{context.get('greeting', 'Hello')}, {name}!"


def highlight(text, word):
    parts = [escape(part) for part in text.split(word)]
    return (Markup("<mark>%s</mark>") % word).join(parts)


def make_env(currency="£"):
    env = Environment(autoescape=True)
    env.globals["currency"] = currency
    env.filters["money"] = money
    env.filters["greet"] = greet
    env.filters["highlight"] = highlight
    return env


def render(source, currency="£", **values):
    return make_env(currency).from_string(source).render(**values)

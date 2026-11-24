from app.render import highlight, render


def test_other_currency_and_default_greeting():
    assert render("{{ 9876543.219|money }}", currency="$") == "$9,876,543.22"
    assert render("{{ 0|money }}") == "£0.00"
    assert render("{{ 'Bo'|greet }}") == "Hello, Bo!"


def test_plain_values_are_escaped():
    assert render("<p>{{ name }}</p>", name="<script>x</script>") == "<p>&lt;script&gt;x&lt;/script&gt;</p>"
    assert render("{{ name|greet }}", name="<i>", greeting="Hey") == "Hey, &lt;i&gt;!"


def test_highlight_directly():
    out = highlight("I <3 tea, <3!", "<3")
    assert hasattr(out, "__html__")
    assert str(out) == "I <mark>&lt;3</mark> tea, <mark>&lt;3</mark>!"
    assert str(highlight("no match here", "zzz")) == "no match here"

from app.render import render


def test_money_and_greet():
    out = render("{{ total|money }} - {{ 'Ann'|greet }}", total=1234.5, greeting="Hi")
    assert out == "£1,234.50 - Hi, Ann!"


def test_highlight_escapes():
    out = render("{{ text|highlight('cat') }}", text="<b>cat</b> & cat")
    assert out == "&lt;b&gt;<mark>cat</mark>&lt;/b&gt; &amp; <mark>cat</mark>"

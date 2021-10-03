from raspar.wrappers import follow, field

@follow
def some_function(urls):
    for url in urls:
        yield url


def test_follow():
    urls = [
        "i_am_cool.com/a",
        "i@am@bad"
    ]

    assert some_function(urls) == ["http://www.i_am_cool.com/a"]


def test_field()
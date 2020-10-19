import pytest
import t61codec

# NOTE: This cannot be undone in Py<3.10 (see
# https://bugs.python.org/issue41842) so we just call this on the module-level
t61codec.register()


@pytest.mark.parametrize(
    "lookup_name, expected_name",
    [("t61", "t.61"), ("t.61", "t.61"), ("utf8", "utf-8")],
)
def test_search(lookup_name, expected_name):
    result = t61codec.search_function(lookup_name)
    assert result.name == expected_name

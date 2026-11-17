from custom_components.shoebox.const import DOMAIN


def test_domain_matches_folder() -> None:
    assert DOMAIN == "shoebox"

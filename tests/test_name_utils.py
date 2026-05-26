"""Tests for name normalization utilities."""

from adg_agent_sdk.name_utils import (
    normalize_project_name,
    project_name_to_dir,
    project_name_to_package,
    validate_package_name,
)


class TestNormalizeProjectName:
    def test_simple_name(self) -> None:
        assert normalize_project_name("my-project") == "my-project"

    def test_spaces_to_hyphens(self) -> None:
        assert normalize_project_name("My Agent App") == "my-agent-app"

    def test_leading_trailing_whitespace(self) -> None:
        assert normalize_project_name("  hello  ") == "hello"

    def test_special_chars_to_hyphens(self) -> None:
        assert normalize_project_name("hello@world!") == "hello-world"

    def test_multiple_hyphens_collapsed(self) -> None:
        assert normalize_project_name("a---b__c") == "a-b-c"

    def test_empty_returns_default(self) -> None:
        assert normalize_project_name("") == "my-project"

    def test_only_special_chars_returns_default(self) -> None:
        assert normalize_project_name("!!!") == "my-project"


class TestProjectNameToDir:
    def test_kebab_case(self) -> None:
        assert project_name_to_dir("My App") == "my-app"


class TestProjectNameToPackage:
    def test_converts_to_snake_case(self) -> None:
        assert project_name_to_package("my-app") == "my_app"

    def test_spaces_to_underscores(self) -> None:
        assert project_name_to_package("My App") == "my_app"

    def test_leading_digit_default(self) -> None:
        assert project_name_to_package("123app") == "my_app"


class TestValidatePackageName:
    def test_valid_name(self) -> None:
        assert validate_package_name("my_app") is None
        assert validate_package_name("_hidden") is None

    def test_empty(self) -> None:
        assert validate_package_name("") is not None

    def test_starts_with_digit(self) -> None:
        assert validate_package_name("1app") is not None

    def test_invalid_chars(self) -> None:
        assert validate_package_name("my-app") is not None

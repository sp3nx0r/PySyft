# stdlib
import re
from types import MethodType
from typing import Any

# relative
from ..types.dicttuple import DictTuple
from ..types.syft_object import SyftObject


def _patch_ipython_sanitization() -> None:
    try:
        # third party
        from IPython import get_ipython
    except ImportError:
        return

    ip = get_ipython()
    if ip is None:
        return

    # stdlib
    from importlib import resources

    # third party
    import nh3

    # relative
    from .util.assets import load_css
    from .util.assets import load_js
    from .util.notebook_ui.styles import CSS_CODE
    from .util.notebook_ui.styles import FONT_CSS
    from .util.notebook_ui.styles import ITABLES_CSS
    from .util.notebook_ui.styles import JS_DOWNLOAD_FONTS

    tabulator_js = load_js("tabulator.min.js")
    tabulator_js = tabulator_js.replace(
        "define(t)", "define('tabulator-tables', [], t)"
    )

    SKIP_SANITIZE = [
        FONT_CSS,
        ITABLES_CSS,
        CSS_CODE,
        JS_DOWNLOAD_FONTS,
        tabulator_js,
        load_css("tabulator_pysyft.min.css"),
        load_js("table.js"),
    ]

    css_reinsert = f"""
<style>{FONT_CSS}</style>
<style>{ITABLES_CSS}</style>
{JS_DOWNLOAD_FONTS}
{CSS_CODE}
"""

    escaped_js_css = re.compile(
        "|".join(re.escape(substr) for substr in SKIP_SANITIZE),
        re.IGNORECASE | re.MULTILINE,
    )

    table_template = (
        resources.files("syft.assets.jinja").joinpath("table.jinja2").read_text()
    )
    table_template = table_template.strip()
    table_template = re.sub(r"\\{\\{.*?\\}\\}", ".*?", re.escape(table_template))
    escaped_template = re.compile(table_template, re.DOTALL | re.VERBOSE)

    def display_sanitized_html(obj: SyftObject | DictTuple) -> str | None:
        if hasattr(obj, "_repr_html_") and callable(obj._repr_html_):  # type: ignore
            _str = obj._repr_html_()  # type: ignore
            matching_template = escaped_template.findall(_str)
            _str = escaped_template.sub("", _str)
            _str = escaped_js_css.sub("", _str)
            _str = nh3.clean(_str)
            return f"{css_reinsert} {_str} {"\n".join(matching_template)}"
        return None

    def display_sanitized_md(obj: SyftObject) -> None:
        if hasattr(obj, "_repr_markdown_"):
            return nh3.clean(obj._repr_markdown_())

    ip.display_formatter.formatters["text/html"].for_type(
        SyftObject, display_sanitized_html
    )
    ip.display_formatter.formatters["text/html"].for_type(
        DictTuple, display_sanitized_html
    )
    ip.display_formatter.formatters["text/markdown"].for_type(
        SyftObject, display_sanitized_md
    )


def _patch_ipython_autocompletion() -> None:
    try:
        # third party
        from IPython import get_ipython
        from IPython.core.guarded_eval import EVALUATION_POLICIES
    except ImportError:
        return

    ipython = get_ipython()
    if ipython is None:
        return

    try:
        # this allows property getters to be used in nested autocomplete
        ipython.Completer.evaluation = "limited"
        ipython.Completer.use_jedi = False
        policy = EVALUATION_POLICIES["limited"]

        policy.allowed_getattr_external.update(
            [
                ("syft.client.api", "APIModule"),
                ("syft.client.api", "SyftAPI"),
            ]
        )
        original_can_get_attr = policy.can_get_attr

        def patched_can_get_attr(value: Any, attr: str) -> bool:
            attr_name = "__syft_allow_autocomplete__"
            # first check if exist to prevent side effects
            if hasattr(value, attr_name) and attr in getattr(value, attr_name, []):
                if attr in dir(value):
                    return True
                else:
                    return False
            else:
                return original_can_get_attr(value, attr)

        policy.can_get_attr = patched_can_get_attr
    except Exception:
        print("Failed to patch ipython autocompletion for syft property getters")

    try:
        # this constraints the completions for autocomplete.
        # if __syft_dir__ is defined we only autocomplete those properties
        original_attr_matches = ipython.Completer.attr_matches

        def patched_attr_matches(self, text: str) -> list[str]:  # type: ignore
            res = original_attr_matches(text)
            m2 = re.match(r"(.+)\.(\w*)$", self.line_buffer)
            if not m2:
                return res
            expr, _ = m2.group(1, 2)
            obj = self._evaluate_expr(expr)
            if isinstance(obj, SyftObject) and hasattr(obj, "__syft_dir__"):
                # here we filter all autocomplete results to only contain those
                # defined in __syft_dir__, however the original autocomplete prefixes
                # have the full path, while __syft_dir__ only defines the attr
                attrs = set(obj.__syft_dir__())
                new_res = []
                for r in res:
                    splitted = r.split(".")
                    if len(splitted) > 1:
                        attr_name = splitted[-1]
                        if attr_name in attrs:
                            new_res.append(r)
                return new_res
            else:
                return res

        ipython.Completer.attr_matches = MethodType(
            patched_attr_matches, ipython.Completer
        )
    except Exception:
        print("Failed to patch syft autocompletion for __syft_dir__")


def patch_ipython() -> None:
    _patch_ipython_sanitization()
    _patch_ipython_autocompletion()

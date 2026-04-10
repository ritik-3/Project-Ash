from project_ash.automation.router import TargetType, choose_route


def test_browser_route_selected() -> None:
    decision = choose_route(action="open_website", has_dom_target=True, has_desktop_target=False)
    assert decision.target == TargetType.BROWSER


def test_desktop_route_selected() -> None:
    decision = choose_route(action="open_app", has_dom_target=False, has_desktop_target=True)
    assert decision.target == TargetType.DESKTOP


def test_fallback_route_selected() -> None:
    decision = choose_route(action="unknown", has_dom_target=False, has_desktop_target=False)
    assert decision.target == TargetType.VISION_FALLBACK

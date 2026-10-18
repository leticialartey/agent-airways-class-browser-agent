"""
Test program for Team 02's set_checkbox tool.
Run it from the project folder with:  python test_set_checkbox.py
"""

import json
import browser_tools
from team_tools import set_checkbox

passed = 0
failed = 0


def check(description, condition):
    # Records one test result as PASS or FAIL.
    global passed, failed
    if condition:
        passed = passed + 1
        print("PASS:", description)
    else:
        failed = failed + 1
        print("FAIL:", description)


def try_tool(argument):
    # Does what the agent will do: validate first, run only if valid.
    print()
    print("PROPOSAL:  ", json.dumps({"action": "set_checkbox", "argument": argument}))
    is_valid, reason = set_checkbox.validate(argument)
    print("VALIDATION:", is_valid, "-", reason)
    if not is_valid:
        print("ACTION:     none (blocked before touching the browser)")
        return {"ok": False, "message": reason, "data": {}}
    result = set_checkbox.run(browser_tools.page, argument, {})
    print("RESULT:    ", json.dumps(result))
    return result


def main():
    browser_tools.start_browser()
    page = browser_tools.page
    page.goto(browser_tools.SITE_URL)

    # Test 1: wrong screen. The bag checkbox is not usable on the search screen.
    print("\n=== Test 1: calling the tool on the search screen (should fail safely) ===")
    result = try_tool({"field": "checked_bag", "checked": True})
    check("Tool reports failure when the checkbox is not on the current screen", result["ok"] == False)

    # Pause so you can click through the site by hand in the Playwright window.
    print()
    input("In the Playwright browser window, search for a flight, choose a flight and a seat, "
          "and continue until you see the passenger details screen. Then press Enter here... ")

    bag = page.locator("#checkedBag")

    # Test 2: check the bag box, then confirm with ur own separate read of the page.
    print("\n=== Test 2: set checked_bag to True ===")
    result = try_tool({"field": "checked_bag", "checked": True})
    actual = bag.is_checked()
    print("INDEPENDENT CHECK: the browser says checkedBag is", actual)
    check("checked_bag is True on the page", result["ok"] == True and actual == True)
    
    # Save a picture of the page as evidence, then pause so a person can see it.
    page.screenshot(path="evidence_bag_checked.png")
    page.wait_for_timeout(2000)

    # Test 3: uncheck it again and confirm.
    print("\n=== Test 3: set checked_bag to False ===")
    result = try_tool({"field": "checked_bag", "checked": False})
    actual = bag.is_checked()
    print("INDEPENDENT CHECK: the browser says checkedBag is", actual)
    check("checked_bag is False on the page", result["ok"] == True and actual == False)
    page.screenshot(path="evidence_bag_unchecked.png")
    page.wait_for_timeout(2000)

    # Test 4: unknown checkbox name must be refused, and nothing on the page changes.
    print("\n=== Test 4: unknown checkbox name (should be refused) ===")
    before = bag.is_checked()
    result = try_tool({"field": "credit_card", "checked": True})
    after = bag.is_checked()
    print("INDEPENDENT CHECK: checkedBag before =", before, ", after =", after)
    check("Unknown name is refused and the page is unchanged", result["ok"] == False and before == after)

    # Test 5: checked='yes' (text, not a Boolean) must be refused.
    print("\n=== Test 5: checked='yes' instead of True (should be refused) ===")
    before = bag.is_checked()
    result = try_tool({"field": "checked_bag", "checked": "yes"})
    after = bag.is_checked()
    print("INDEPENDENT CHECK: checkedBag before =", before, ", after =", after)
    check("Text 'yes' is refused and the page is unchanged", result["ok"] == False and before == after)

    print("\n=== Summary:", passed, "passed,", failed, "failed ===")
    input("Press Enter to close the browser... ")


try:
    main()
finally:
    browser_tools.close_browser()

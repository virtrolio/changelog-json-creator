"""
Have you ever wanted to take your Google Docs changelog bulleted lists and automatically create a new json object so
that you can deploy the changelog update easily to a website (e.g. Virtrolio)? Your solution hath come!

How to use this script:
- Ensure that this script is in the same folder as...
  - A changelog.json file that you want to update
  - A changelogInput.txt file where you will copy paste the changelog items into
- Go to the Google Docs that has your changelog, copy paste the bullet list items, and paste into changelogInput.txt
- Run the python script
- By the end of it, your changelog.json will have been updated with the new update content!
"""

import codecs
import json
import datetime
import re

CHANGELOG_INPUT_FILE = "changelogInput.txt"
CHANGELOG_OUTPUT_FILE = "changelog.json"

# CSS selectors for each type of 'tag' a changelog-item can have
css_selectors = {
    "NEW": "changelog-new",
    "UPD": "changelog-upd",
    "FIX": "changelog-fix"
}

# 'Locations' on the website a changelog item can refer to
allowed_locations = ['Sitewide', 'Signing', 'MyVirtrolio', 'About', 'Legal', 'Navbar', 'Viewing', 'FAQ', 'Footer',
                     'Home']


def extract_data():
    """
    Extract data from changelogInput.txt and changelog.json files.
    :return: array of items inputted into changelogInput.txt
    :return: JSON content extracted as an array of dictionaries
    """
    try:
        with codecs.open(CHANGELOG_INPUT_FILE, encoding='utf-8') as log_file:  # utf-8 encoding allows for emojis!
            # Extract lines of input text file
            input_items = log_file.readlines()
            if not input_items:
                raise ValueError(CHANGELOG_INPUT_FILE + " is empty")
    except FileNotFoundError:
        raise FileNotFoundError(CHANGELOG_INPUT_FILE + "not found in current directory.")

    try:
        with codecs.open(CHANGELOG_OUTPUT_FILE, encoding='utf-8') as changelogJSON:
            # Extract current changelog JSON into dictionary array
            changelog = json.load(changelogJSON)
    except FileNotFoundError:
        raise FileNotFoundError(CHANGELOG_OUTPUT_FILE + "not found in current directory.")

    # In case changelog.json is not formatted as a proper JSON object or array of JSON objects
    except json.JSONDecodeError:

        # Allow JSONDecode Error is triggered by an empty file, in which case an array can be initialized
        with open(CHANGELOG_OUTPUT_FILE, "r+") as f:
            json_content = f.read()

            if json_content == "":
                input(CHANGELOG_OUTPUT_FILE + " is empty. Press enter to add an empty array [] to hold your updates: ")
                f.write("[]")
                changelog = []  # Adds empty array to JSON
            else:
                raise json.JSONDecodeError

    return input_items, changelog


def create_changelog_item(input_item):
    """
    Take input item and extract content properly to create a dictionary (aka JSON object) for changelog.json
    :param input_item: A string representing one line from changelogInput.txt
    :return: input_item reformatted into a dictionary (aka JSON object)
    """

    pattern = re.compile("(?:\[(\w{3})\])(?: (\(BETA\)))? (\w+): (.+)")  # Use RegEx to match each item
    match = pattern.match(input_item)

    if match:
        item_type, beta_flag, location, item_content = match.groups()  # Extract captured groups from RegEx match
    else:
        raise ValueError("RegEx matching failed for following item, please follow '[TAG] Location: Content' format: "
                         + input_item)

    if not (item_type in list(css_selectors.keys())):
        # If the item_type is not one of the allowed keys in the css_selectors dictionary, raise an error
        raise ValueError("Invalid [TAG] for following item, please follow '[TAG] Location: Content' format: "
                         + input_item)

    beta_flag = True if beta_flag else False

    if not (location in allowed_locations):
        raise ValueError("Invalid location used for following item: " + input_item)

    item_type_css = css_selectors[item_type]

    changelog_item = {
        "type": item_type,
        "typeCSS": item_type_css,
        "betaFlag": beta_flag,
        "location": location,
        "content": item_content,
    }

    return changelog_item


def check_version_number(version_number):
    """
    Checks to see if inputted version number follows semantic versioning (e.g. 1.1.0)
    :param version_number: Version number to be checked
    :return: Boolean, whether inputted version number follows the proper format
    """
    numbers = version_number.split(".")

    try:
        return len(numbers) == 3 and [int(i) for i in numbers]
    except ValueError:
        return False


def request_version_number(changelog):
    """
    Checks changelog for the previous version number and generates the appropriate subsequent version number for a
    major / minor / patch update, according to 'Semantic Patching' (details here: https://semver.org/)
    :param changelog: Changelog to search
    :return: Version number to be displayed for this update
    """

    if changelog:
        # If changelog has at least one item in it, try to extract the topmost item's version number
        last_version = changelog[0]["versionNumber"]
        last_release_date = changelog[0]["releaseDate"]
        # TODO: Make sure newline is only if retrying
        print(f"\nYour last version was: {last_version}, released on {last_release_date}.")

        update_type = input("Would you like to push a major, minor, or patch update? Press 1, 2, or 3 respectively: ")

        major, minor, patch = [int(i) for i in last_version.split(".")]

        if update_type == "1":
            major += 1
        elif update_type == "2":
            minor += 1
        elif update_type == "3":
            patch += 1
        else:
            print("Invalid choice. Let's try that again.")
            request_version_number(changelog)

        version_number = ".".join([str(i) for i in [major, minor, patch]])  # Convert numbers to string, join with '.'

        answer = input(f"Your version number would be: {version_number}. Press enter if correct, type something if "
                       f"incorrect: ")

        if answer:
            request_version_number(changelog)

    else:
        print("No previous version found in " + CHANGELOG_OUTPUT_FILE)

        while True:
            # If the changelog has no previous versions, allow the user to choose the first version number
            version_number = input("What version would you like to push? ")

            if check_version_number(version_number):
                break
            else:
                print("The version number you entered does not fit with the X.X.X format, let's try again.\n")

    return version_number


def update_changelog(version_number, release_date, changelog_items, changelog):
    """
    Updates changelog.json with a new update, packaging the appropriately generated version number and each update item
    into a dictionary (aka JSON object) to be inserted into the first index of changelog.json
    :param version_number: Version number to be displayed for this update
    :param release_date: Release date to be displayed for this update
    :param changelog_items: List of changelog items formatted as an array of dictionaries (aka JSON objects)
    :param changelog: changelog dictionary to be updated
    """

    # Determine if the update contains purely beta content
    beta_update = True
    for changelog_item in changelog_items:
        if not changelog_item["betaFlag"]:
            beta_update = False
            break

    # Create a new dictionary and input relevant properties
    update_dictionary = {
        "versionNumber": version_number,
        "releaseDate": release_date,
        "betaUpdate": beta_update,
        "items": changelog_items
    }

    # Insert new update to beginning of changelog dictionary array (so the new entry displays at top on the website)
    changelog.insert(0, update_dictionary)

    # Rewrite JSON file with proper indentation
    with codecs.open(CHANGELOG_OUTPUT_FILE, encoding='utf-8', mode="w+") as changelogJSON:
        changelogJSON.write(json.dumps(changelog, indent=2))


def get_release_date():
    """
    Asks user if they want to use the current date for their update or if they want to enter a date.
    :return: release date to be displayed for the update
    """

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Extract current date into "YYYY-MM-DD" format

    # Ask if user wants to use current date for the update
    use_current_date = input(f"Current date is: {current_date}. Would you like to set this as the release date for"
                             " your update? Type y for yes or something else for no: ")

    if use_current_date.lower() == 'y':
        return current_date
    else:
        while True:
            try:
                # Allow user to input a custom date
                year = int(input("Enter year: "))
                month = int(input("Enter month number (e.g. 3 for March): "))
                day = int(input("Enter day number (e.g. 24 for July 24): "))

                user_date = datetime.datetime(year, month, day).strftime("%Y-%m-%d")
                # Create date with "YYYY-MM-DD" format
                # Using datetime.datetime() here as it will automatically check to see if the numbers are valid

                use_user_date = input(f"\nThe date you inputted is: {user_date}. Is that what you want? Type y for yes"
                                      f" or something else for no: ")

                if use_user_date.lower() == 'y':
                    return user_date
            except ValueError:
                input("Invalid input: please enter numbers. Press enter to try again.\n")


def main():
    input_items, changelog = extract_data()  # Extract data from files

    changelog_items = []

    for input_item in input_items:
        changelog_items.append(create_changelog_item(input_item))  # Convert input data into JSON objects

    version_number = request_version_number(changelog)
    release_date = get_release_date()

    update_changelog(version_number, release_date, changelog_items, changelog)  # Update changelog.json with new data

    print(f"Program has completed successfully. Check {CHANGELOG_OUTPUT_FILE} to see if it has updated properly.")


if __name__ == "__main__":
    main()

"""
Have you ever wanted to take your Google Docs changelog bulleted lists and automatically create a new json object so
that you can deploy the changelog update easily to Virtrolio? Your solution hath come!

How to use this script:
- Ensure that this script is in the same folder as...
  - The changelog.json that you want to update
  - The changelogInput.txt where you will copy paste the changelog items into
- Go to the Google Docs with your changelog, copy paste the bullet list items, and paste into changelogInput.txt
- Run the python script
- Voilà, your changelog.json has now been updated with the new update content! Update the changelog.json on the server
  and the changelog modal on the website will automatically format the newest update properly

"""

import codecs
import json


def extract_data():
    """
    Extract data from changelogInput.txt and changelog.json files.
    :return: input_items: array of items inputted into changelogInput.txt
    :return: JSON content extracted as an array of dictionaries
    """
    try:
        with codecs.open("changelogInput.txt", encoding='utf-8') as log_file:  # utf-8 encoding allows for emojis!
            # Extract lines of input text file
            input_items = log_file.readlines()
            if not input_items:
                raise ValueError("changelogInput.txt is empty")
    except FileNotFoundError:
        raise FileNotFoundError("'changelogInput.txt' not found in current directory.")

    try:
        with codecs.open("changelog.json", encoding='utf-8') as changelogJSON:
            # Extract current changelog JSON into dictionary array
            changelog = json.load(changelogJSON)
    except FileNotFoundError:
        raise FileNotFoundError("'changelog.json' not found in current directory.")

    except json.JSONDecodeError:
        with open("changelog.json") as f:
            json_content = f.read()

        if json_content == "":
            input("changelog.json is empty. Press enter to add an empty array [] to hold your updates: ")
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
    item_type, itemNoTag = input_item[0:5], input_item[5:]

    try:
        location, content = itemNoTag.split(":", 1)[0].strip(), itemNoTag.split(":", 1)[1].strip()
    except IndexError:
        raise IndexError("No location found for following item, use [TAG] Location: Content format: " + input_item)

    allowed_locations = ['Sitewide', 'Signing', 'My Virtrolio', 'About Us',
                         'Legal', 'Navbar', 'Viewing', 'FAQ', 'Footer']

    if not (location in allowed_locations):
        raise ValueError("Invalid location used for this item: " + input_item)

    if item_type == "[NEW]":
        item_type = "NEW"
        item_type_CSS = "changelog-new"
    elif item_type == "[UPD]":
        item_type = "UPD"
        item_type_CSS = "changelog-upd"
    elif item_type == "[FIX]":
        item_type = "FIX"
        item_type_CSS = "changelog-fix"
    else:
        raise ValueError("Invalid [TAG] for item, lease follow '[TAG] Location: Content' format: " + input_item)

    changelog_item = {
        "type": item_type.strip(),
        "typeCSS": item_type_CSS,
        "location": location.strip(),
        "content": content.strip(),
    }

    return changelog_item


def request_version_number(changelog):
    """
    Checks changelog for the previous version number and requests user for new version number.
    :param changelog: Changelog to search
    :return: Version number to be displayed for this update
    """

    # TODO: generates the appropriate subsequent version number for a major update / minor update / patch update,
    #  according to 'Semantic Patching' (details here: https://semver.org/)

    if changelog:
        # If changelog has at least one item in it, try to extract the topmost item's version number
        last_version = changelog[0]["versionNumber"]
        print("Your last version was: ", last_version)
    else:
        # If the changelog is empty, assume that you want to push
        print("No previous version found in changelog.json.")

    version_number = input("What version would you like to push? ")

    return version_number


def update_changelog(version_number, changelog_items, changelog):
    """
    Updates changelog.json with a new update, packaging the appropriately generated version number and each update item
    into a dictionary (aka JSON object) to be inserted into the first index of changelog.json
    :param version_number: Version number to be displayed for this update
    :param changelog_items: List of changelog items formatted as an array of dictionaries (aka JSON objects)
    :param changelog: changelog dictionary to be updated
    """
    # Create a new dictionary (aka JSON object) and input relevant properties
    updateDictionary = {
        "versionNumber": "v" + version_number,
        "items": changelog_items
    }

    # Insert new update to beginning of changelog dictionary array (so the new entry displays at top on the website)
    changelog.insert(0, updateDictionary)

    # Rewrite JSON file with proper indentation
    with codecs.open("changelog.json", encoding='utf-8', mode="w+") as changelogJSON:
        changelogJSON.write(json.dumps(changelog, indent=2))


def main():
    input_items, changelog = extract_data()

    changelog_items = []

    for input_item in input_items:
        changelog_items.append(create_changelog_item(input_item))

    version_number = request_version_number(changelog)
    update_changelog(version_number, changelog_items, changelog)
    print("Program complete successfully. Check changelog.json to see if it has updated properly.")


if __name__ == "__main__":
    main()

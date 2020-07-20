# changelog-json-creator

Have you ever wanted to take your Google Docs changelog bulleted lists and automatically create a new json object so
that you can deploy the changelog update easily to a website (e.g. Virtrolio)? Your solution hath come!
How to use this script:
- Ensure that this script is in the same folder as...
  - A changelog.json file that you want to update
  - A changelogInput.txt file where you will copy paste the changelog items into
- Go to the Google Docs that has your changelog, copy paste the bullet list items, and paste into changelogInput.txt
- Run the python script
- By the end of it, your changelog.json will have been updated with the new update content!

codeunbox
=========

CodeUnBox: Export CodeBox snippet data via a simple Python script

If you need to migrate your data out of CodeBox, this script will
help you do it.

It's an ugly parse of a CoreData XML format file, but it does the
job sufficiently well to migrate.

So far, I can extract all the relevant data into Python data dicts
and I'm targeting export to Dash app, which I'm moving to.

In other words, you are going from this:
https://itunes.apple.com/us/app/codebox/id412536790

To this:
https://itunes.apple.com/us/app/dash-docs-snippets/id458034879

- Marc
# Category Checker

Track number of products in all categories and report if there is a significant decreaes.

## Installation

```
git clone https://github.com/Skywire/CategoryChecker.git ~/CategoryChecker
cd CategoryChecker
[python3 executable] -m pip install -r requirements.txt
```

## Usage

### Generate snapshot

`[python3 executable] ~/CategoryChecker/main.py generate [path to n98-magerun] [path to magento root]`

### Analyse snapshots

Percentage trigger defaults to 50%, but can be set with an argument

`[python3 executable] ~/CategoryChecker/main.py analyse [recipient] [percentage trigger]`
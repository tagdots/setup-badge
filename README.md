# Setup-Badge

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10951/badge)](https://www.bestpractices.dev/projects/10951)
[![CI](https://github.com/tagdots/setup-badge/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots/setup-badge/actions/workflows/ci.yaml)
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/coverage.json)](https://github.com/tagdots/setup-badge/actions/workflows/cron-tasks.yaml)

<br>

## 😎 Why you need setup-badge?

**Setup-Badge** creates `dynamic` and `static` endpoint badges to showcase on your README file. These badges can highlight key aspects such as `build status`, `code coverage percentage`, `software version`, `license` and more.

<br>

**Note**

- dynamic badge changes over time (e.g. code coverage percentage and software version)
- static badge doesn't change over time (e.g. license and programming language)

<br>

## ⭐ How setup-badge works

Under the hood, **setup-badge** creates a [shields.io endpoint badge](https://shields.io/badges/endpoint-badge), which is composed of _a shields.io endpoint_ and _an URL to your JSON file (JSON Endpoint)_.

```
![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/badge.json)
```

#### setup-badge workflow is outlined below.

1. **setup-badge** runs with [command line options](https://github.com/tagdots/setup-badge#-run-setup-badge-command-line-options).
1. **setup-badge** adds/updates a json file from your options.
1. **setup-badge** pushes a commit to the remote branch.
1. **endpoint badge** is created with `shields.io endpoint` and `your json file`.

Afterwards, you can put `endpoint badge` into your README file.

![How It Works](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/assets/setup-badge.png)

<br>

## 🎉 Use Case 1️⃣ - running on GitHub action

### Summary: create multiple static badges

**setup-badge**:

- runs `on demand`
- creates two static badges: `language` and `license`
  - language badge does not have a badge url
  - license badge has a badge url that links to the project's LICENSE file

### Example: create multiple static badges

```
name: setup-badge

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  language-badge:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    steps:
    - id: language-badge
      uses: tagdots/setup-badge@<commit sha> # 1.2.3
      with:
        badge-name: language
        label: Language
        message: Python
        message-color: FFA500

  license-badge:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    steps:
    - id: license-badge
      uses: tagdots/setup-badge@<commit sha> # 1.2.3
      with:
        badge-name: license
        badge-url: https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE
        label: License
        message: MIT
        message-color: FFA500
```

<br><br>

### Summary: create a dynamic badge

**setup-badge**:

- runs `on schedule at 5:30 pm UTC` or `on demand`
- runs a coverage test and get the coverage percentage from the test result
- creates a dynamic `Code Coverage` badge with the coverage % that changes over time

### Example: create a dynamic badge

```
name: setup-badge

on:
  schedule:
    - cron: '30 17 * * *'

  workflow_dispatch:

permissions:
  contents: read

jobs:
  coverage-badge:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    outputs:
      COV_PER: ${{ steps.get-coverage-results.outputs.COV_PER }}

    steps:
    - id: coverage-run
      run: coverage run

    - id: get-coverage-results
      run: |
        echo "COV_PER=$(...coverage run results...)" >> "$GITHUB_OUTPUT"

    - id: coverage-badge
      uses: tagdots/setup-badge@<commit sha> # 1.2.3
      with:
        badge-name: coverage
        label: "Code Coverage"
        message: "${{ steps.get-coverage-results.outputs.COV_PER }}"
```

<br>

## 🎉 Use Case 2️⃣ - running CLI locally

In this use case, you run **setup-badge** manually with the steps below:

1. install **setup-badge**.
1. run **setup-badge**.

<br>

### 🔆 install setup-badge

In the example below, we first install **setup-badge** in a Python virtual environment.

```
~/work/<your project> $ uv pip install -U setup-badge
```

<br>

### 🔧 run setup-badge command line options

| Input             | Description                  | Default                | Notes                                                              |
| ----------------- | ---------------------------- | ---------------------- | ------------------------------------------------------------------ |
| `badge-name`      | JSON endpoint filename       | `badge`                | JSON endpoint filename                                             |
| `branch-name`     | Branch to hold JSON endpoint | `badges`               | a single branch can hold multiple JSON endpoint files              |
| `badge-style`     | Badge style                  | `flat`                 | other options: `flat-square`, `plastic`, `for-the-badge`, `social` |
| `badge-url`       | Badge URL                    | `''`                   | no default value (enter a url if necessary)                        |
| `label`           | Left side text               | `demo`                 | -                                                                  |
| `label-color`     | Left side background color   | `2e2e2e`               | hex color                                                          |
| `message`         | Right side text              | `no status`            | place dynamic/static data here                                     |
| `message-color`   | Right side background color  | `2986CC`               | hex color                                                          |
| `remote-name`     | Git remote source branch     | `origin`               | leave it as-is in general                                          |
| `gitconfig-name`  | Git config user name         | `Mona Lisa`            | need this option for CI or GitHub action                           |
| `gitconfig-email` | Git config user email        | `mona.lisa@github.com` | need this option for CI or GitHub action                           |

<br><br>

🏃 _**CLI Options**_: `--badge-name license --label License --message MIT --message-color FFA500 --badge-url https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE`

```
~/work/<your project> $ uv run setup-badge --badge-name license --label License --message MIT --message-color FFA500 --badge-url https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE

🚀 Starting to create a badge (license.json) in branch (badges)...

✅ validated inputs from command line options
✅ checkout local branch (badges)
✅ created badges/license.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (dd8906c) to remote branch (badges)

🎉 Endpoint Badge: [![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/license.json)](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE)
🤩 Branch restored to original active branch: main
```

_**Endpoint Badge**_<br>
[![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/license.json)](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE)

<br><br>

🏃 _**CLI Options**_: `--badge-name marketplace --label Marketplace --message setup-badge --message-color FF6360 --badge-url https://github.com/marketplace/actions/setup-badge`

```
(setup-badge) ~/work/setup-badge $ setup-badge --badge-name marketplace --label Marketplace --message setup-badge --message-color FF6360 --badge-url https://github.com/marketplace/actions/setup-badge

🚀 Starting to create a badge (marketplace.json) in branch (badges)...

✅ validated inputs from command line options
✅ checkout local branch (badges)
✅ created badges/marketplace.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (8991c28) to remote branch (badges)

🎉 Endpoint Badge: [![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge)
🤩 Branch restored to original active branch: main
```

_**Endpoint Badge**_<br>
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge)

<br><br>

### ✨ Summary of running the above commands

- **badges** branch can hold multiple JSON files.
- **badges** folder can hold json files from different branches.

![Command Runs](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/assets/badges-folder.png)

<br><br>

## 🔔 What is next after creating the endpoint badge?

- copy `endpoint badge` output and paste to your README file
- write a commit and merge your code

<br><br>

## 😕 Troubleshooting

Open an [issue][issues]

<br>

## 🙏 Contributing

For pull requests to be accepted on this project, you should follow [PEP8][pep8] when creating/updating Python codes.

See [Contributing][contributing]

<br>

## 🙌 Appreciation

If you find this project helpful, please ⭐ star it. **Thank you**.

<br>

## 📚 References

[Shields.io Endpoint Badge](https://shields.io/badges/endpoint-badge)

[Hex Color](https://www.color-hex.com/)

[How to fork a repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

<br>

[contributing]: https://github.com/tagdots/setup-badge/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots/setup-badge/issues
[pep8]: https://google.github.io/styleguide/pyguide.html

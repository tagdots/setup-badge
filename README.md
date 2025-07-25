# setup-badge

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10951/badge)](https://www.bestpractices.dev/projects/10951)
[![CI](https://github.com/tagdots/setup-badge/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots/setup-badge/actions/workflows/ci.yaml)
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge-action)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/coverage.json)](https://github.com/tagdots/setup-badge/actions/workflows/cron-tasks.yaml)

<br>

## 😎 Why you need setup-badge?
**setup-badge** empowers you to create `dynamic` and `static` endpoint badges to showcase on your README file.

In a dynamic badge, the `message` changes over time.  e.g. code coverage percentage and software version.  In a static badge, the `message` does not change regularly over time.  e.g. license and programming language.

_p.s. `message` refers to the right side of a badge_

<br>

## ⭐ How setup-badge works

Under the hood, **setup-badge** creates a [shields.io endpoint badge](https://shields.io/badges/endpoint-badge), which is composed of _a shields.io endpoint_ and _an URL to your JSON file (JSON Endpoint)_.

```
![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/badge.json)
```

#### Overall workflow is outlined below.

1. **setup-badge** runs with [command line options](https://github.com/tagdots/setup-badge?tab=readme-ov-file#-setup-badge-command-line-options).
1. **setup-badge** adds/updates a json file from your options.
1. **setup-badge** pushes a commit to the remote branch.
1. **endpoint badge** is created with `shields.io endpoint` and `your json file`.

Now, you are ready to put `endpoint badge` into your README file.

![How It Works](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/assets/setup-badge.png)

<br>

## Use Case 1️⃣ - running on GitHub action
In this use case, you run our **setup-badge-action** in a workflow to create badge(s).

Please visit our GitHub action ([setup-badge-action](https://github.com/marketplace/actions/setup-badge-action)) on the `GitHub Marketplace` for details.

<br>

## Use Case 2️⃣ - running locally on your computer
In this use case, you run **setup-badge** manually with the steps below:

1. install **setup-badge**.
1. run **setup-badge**.

<br>

### 🔆 install setup-badge

In the example below, we first install **setup-badge** in a Python virtual environment.

```
~/work/badge-test $ workon badge-test
(badge-test) ~/work/badge-test $ pip install -U setup-badge
```

<br>

### 🔍 run setup-badge

Next, we run **setup-badge** with different options and display the results.

<br>

🏃 _**Run to display command line options**_: `--help`

```
(badge-test) ~/work/badge-test $ setup-badge --help
Usage: setup-badge [OPTIONS]

Options:
  --badge-name TEXT       default: badge
  --badge-branch TEXT     default: badges
  --badge-url TEXT        default: ''
  --badge-style TEXT      default: flat (flat, flat-square, plastic, for-the-badge, social)
  --label TEXT            default: demo (badge left side text)
  --label-color TEXT      default: 2e2e2e (badge left side hex color)
  --message TEXT          default: no status (badge right side text)
  --message-color TEXT    default: 2986CC (badge right side hex color)
  --remote-name TEXT      default: origin
  --gitconfig-name TEXT   default: Mona Lisa
  --gitconfig-email TEXT  default: mona.lisa@github.com
  --version               Show the version and exit.
  --help                  Show this message and exit.
```

<br><br>

🏃 _**Run to create a demo badge**_: `with default command line options`

```
(badge-test) ~/work/badge-test $ setup-badge

🚀 Starting to create a badge.json in branch (badges)...

✅ validated inputs from command line options
✅ checkout local branch (badges)
✅ created badges/badge.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (f9c751c) to remote branch (badges)

🎉 Endpoint Badge: ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/badge.json)
```

_**Endpoint Badge**_<br>
![demo](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/badge.json)

<br><br>

🏃 _**Run to create a license badge**_: `--badge-name license --label License --message MIT --message-color FFA500 --badge-url https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE`

```
(badge-test) ~/work/badge-test $ setup-badge --badge-name license --label License --message MIT --message-color FFA500 --badge-url https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE

🚀 Starting to create a badge (license.json) in branch (badges)...

✅ validated inputs from command line options
✅ checkout local branch (badges)
✅ created badges/badge.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (dd8906c) to remote branch (badges)

🎉 Endpoint Badge: [![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/license.json)](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE)
```

_**Endpoint Badge**_<br>
[![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/license.json)](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/LICENSE)

<br><br>

🏃 _**Run to create a marketplace badge**_: `--badge-name marketplace --label Marketplace --message setup-badge-action --message-color FF6360 --badge-url https://github.com/marketplace/actions/setup-badge-action`

```
(badge-test) ~/work/badge-test $ setup-badge --badge-name marketplace --label Marketplace --message setup-badge-action --message-color FF6360 --badge-url https://github.com/marketplace/actions/setup-badge-action

🚀 Starting to create a badge (marketplace.json) in branch (badges)...

✅ validated inputs from command line options
✅ checkout local branch (badges)
✅ created badges/badge.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (8991c28) to remote branch (badges)

🎉 Endpoint Badge: [![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge-action)
```

_**Endpoint Badge**_<br>
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge-action)

<br><br>

### ✨ Summary of running the above commands

- **badges** branch can hold multiple JSON files.
- **badges** folder can hold json files from different branches.

![Command Runs](https://raw.githubusercontent.com/tagdots/setup-badge/refs/heads/main/assets/badges-folder.png)

<br><br>

## 🔔 What is next after creating the endpoint badge?

- copy and paste to your README file
- write a commit and merge your code

<br><br>

## 🔧 setup-badge command line options

| Input | Description | Default | Notes |
|-------|-------------|----------|----------|
| `badge-name` | JSON endpoint filename | `badge` | JSON endpoint filename |
| `branch-name` | Branch to hold JSON endpoint | `badges` | a single branch can hold multiple JSON endpoint files |
| `badge-style` | Badge style | `flat` | other options: `flat-square`, `plastic`, `for-the-badge`, `social` |
| `badge-url` | Badge URL | `''` | no default value (enter a url if necessary) |
| `label` | Left side text | `demo` | - |
| `label-color` | Left side background color | `2e2e2e` | hex color |
| `message` | Right side text | `no status` | place dynamic/static data here |
| `message-color` | Right side background color | `2986CC` | hex color |
| `remote-name` | Git remote source branch | `origin` | leave it as-is in general |
| `gitconfig-name` | Git config user name | `Mona Lisa` | need this option for CI or GitHub action |
| `gitconfig-email` | Git config user email | `mona.lisa@github.com` | need this option for CI or GitHub action |

<br>

## 😕  Troubleshooting

Open an [issue][issues]

<br>

## 🙏  Contributing

Pull requests and stars are always welcome.  For pull requests to be accepted on this project, you should follow [PEP8][pep8] when creating/updating Python codes.

See [Contributing][contributing]

<br>

## 📚 References

[Shields.io Endpoint Badge](https://shields.io/badges/endpoint-badge)

[Hex Color](https://www.color-hex.com/)

[How to fork a repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

<br>

[contributing]: https://github.com/tagdots/setup-badge/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots/setup-badge/issues
[pep8]: https://google.github.io/styleguide/pyguide.html

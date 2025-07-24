# setup-badge

[![CI](https://github.com/tagdots/setup-badge/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots/setup-badge/actions/workflows/ci.yaml)

<br>

## 😎 Why you need setup-badge?
**setup-badge** empowers you to create `dynamic` and `static` endpoint badges to showcase on your README file.

In a dynamic badge, the `message` changes over time.  For instance, code coverage percentage and software version.  In a static badge, the `message` does not change regularly over time.  For instance, license and programming language.

_p.s. `message` refers to the right side of a badge_

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

[contributing]: https://github.com/tagdots-dev/badge-201/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots-dev/badge-201/issues
[pep8]: https://google.github.io/styleguide/pyguide.html

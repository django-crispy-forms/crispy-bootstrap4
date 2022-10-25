# crispy-bootstrap4

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/smithdc1/crispy-bootstrap4/blob/main/LICENSE)

Bootstrap4 template pack for django-crispy-forms. This template pack was 
included with the core django-crispy-forms package until version 2.0.

## Installation

Install this plugin using `pip`:

```bash
    $ pip install crispy-bootstrap4
```

## Usage

You will need to update your project's settings file to add `crispy_forms`
and `crispy_bootstrap4` to your projects `INSTALLED_APPS`. Also set
`bootstrap4` as and allowed template pack and as the default template pack
for your project:

```python
    INSTALLED_APPS = (
        ...
        "crispy_forms",
        "crispy_bootstrap4",
        ...
    )

    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"

    CRISPY_TEMPLATE_PACK = "bootstrap4"
```

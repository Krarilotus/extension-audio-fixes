"""Neutral module contract: every fix is off unless a profile or plugin turns it on."""
from pathlib import Path
import re

import pytest
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('de', 'en', 'fr', 'ru', 'hu', 'tr', 'ch', 'es', 'fa')
# Option URLs stay unchanged so saved profiles and the "UCP3 Fixes" plugin keep their values.
FEATURES = {
    'startup-sfx-volume': 'startup-sfx-volume',
    'video-fx-volume': 'bink-volume',
    'positional-audio': 'positional-audio',
}


def simple_yaml_scalars(path):
    # The modules' locale files are flat `key: value` maps; no YAML dependency needed.
    entries = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith((' ', '#')):
            key, _, value = line.partition(':')
            entries[key.strip()] = value.strip()
    return entries


def test_options_default_off_with_unchanged_urls():
    text = (ROOT / 'options.yml').read_text(encoding='utf-8')
    urls = re.findall(r'^\s+url: (\S+)$', text, re.M)
    assert urls == [f'audio-fixes.{name}' for name in FEATURES]
    assert re.findall(r'^\s+value: (\S+)$', text, re.M) == ['false'] * len(FEATURES)


def test_version_is_the_neutral_minor_release():
    assert re.search(r'^version: 0\.2\.0$', (ROOT / 'definition.yml').read_text(encoding='utf-8'), re.M)


def run_enable(config):
    lua = LuaRuntime(unpack_returned_tuples=True)
    required = []

    def require(name):
        required.append(name)
        return lua.table_from({'enable': lambda: required.append('enabled ' + name)})

    lua.globals().require = require
    module = lua.execute((ROOT / 'init.lua').read_text(encoding='utf-8'))
    module.enable(module, lua.table_from(config))
    module.enable(module, lua.table_from(config))
    return required


@pytest.mark.parametrize('value', (None, False))
def test_absent_or_false_options_install_nothing(value):
    config = {} if value is None else dict.fromkeys(FEATURES, value)
    assert run_enable(config) == []


@pytest.mark.parametrize('option,feature', FEATURES.items())
def test_each_true_option_installs_only_its_feature_once(option, feature):
    assert run_enable({option: True}) == [feature, 'enabled ' + feature]


def test_locales_and_descriptions_exist_in_all_languages():
    keys = set(simple_yaml_scalars(ROOT / 'locale/en.yml'))
    for language in LANGUAGES:
        assert set(simple_yaml_scalars(ROOT / f'locale/{language}.yml')) == keys, language
        description = (ROOT / f'locale/description-{language}.md').read_text(encoding='utf-8')
        assert description.strip() and '�' not in description, language
        # Every language names the plugin that turns the fixes on.
        assert 'UCP3 Fixes' in description, language

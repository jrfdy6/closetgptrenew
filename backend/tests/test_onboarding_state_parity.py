"""Synthetic outputs from executed frozen TypeScript, not a mirrored Python port."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import unittest

from src.services import onboarding_state as onboarding


FIXTURE_PATH = Path(__file__).parent / 'fixtures/onboarding-state-parity.json'
FIXTURE = json.loads(FIXTURE_PATH.read_text())
FUNCTIONS = {
    'deriveOnboardingState': lambda value: onboarding.derive_onboarding_state(**value),
    'evaluateCapsule': onboarding.evaluate_capsule,
    'classifyGarment': onboarding.classify_garment,
    'hasStyleProfile': onboarding.has_style_profile,
    'ownedBy': onboarding.owned_by,
    'parseDraft': onboarding.parse_draft,
    'timestamp': onboarding.timestamp,
}


def revive(value):
    if isinstance(value, dict):
        if set(value) == {'$number'}:
            return float(value['$number'])
        if set(value) == {'$date'}:
            return datetime.fromisoformat(value['$date'].replace('Z', '+00:00')) if value['$date'] != 'invalid' else None
        return {key: revive(item) for key, item in value.items()}
    return [revive(item) for item in value] if isinstance(value, list) else value


def result(case):
    arguments = [revive(case['input'])]
    if 'extra' in case:
        arguments.append(case['extra'])
    return FUNCTIONS[case['fn']](*arguments)


class OnboardingStateGoldenParityTests(unittest.TestCase):
    def test_fixture_is_anchored_to_accepted_unchanged_typescript(self):
        self.assertEqual(FIXTURE['baseline'], '3ed2ecc472a77406ad13bd1182ac6cf6bf1e797f')
        source = Path(__file__).resolve().parents[2] / FIXTURE['source_path']
        if source.exists():
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), FIXTURE['source_sha256'])

    def test_every_pure_contract_matches_its_frozen_typescript_output(self):
        self.assertEqual(set(FUNCTIONS), {case['fn'] for case in FIXTURE['cases']})
        for case in FIXTURE['cases']:
            with self.subTest(function=case['fn'], case=case['name']):
                self.assertEqual(result(case), case['expected'])


if __name__ == '__main__':
    unittest.main()

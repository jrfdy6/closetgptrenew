"""Real questionnaire formats; no database, provider or network access."""
import unittest
from types import SimpleNamespace

from src.routes.outfit_generation_contract import normalize_generation_user_profile
from src.utils.profile_normalization import normalize_profile_signals


class ProfileSignalsTests(unittest.TestCase):
    def test_real_body_answers_have_specific_paths_without_losing_raw_answers(self):
        for raw, canonical in [("Round/Apple", "apple"), ("Inverted Triangle", "inverted_triangle"),
                               ("Athletic", "athletic"), ("Plus Size", "plus_size")]:
            with self.subTest(raw=raw):
                result = normalize_generation_user_profile({"measurements": {"bodyType": raw}}, "owner")
                self.assertEqual(result["bodyType"], raw)
                self.assertEqual(result["measurements"]["bodyType"], raw)
                self.assertEqual(result["profileSignals"]["body_type"], canonical)

    def test_slider_entire_domain_is_depth_and_never_undertone(self):
        for depth in range(101):
            with self.subTest(depth=depth):
                raw = f"skin_tone_{depth}"
                result = normalize_generation_user_profile({"skinTone": raw})
                self.assertEqual(result["skinTone"], raw)
                signals = result["profileSignals"]
                self.assertEqual(signals["skin_depth_index"], depth)
                self.assertEqual(signals["skin_depth"], "light" if depth <= 33 else "medium" if depth <= 66 else "deep")
                self.assertIsNone(signals["skin_undertone"])

    def test_all_retained_height_ranges_are_interpreted_without_substring_matches(self):
        cases = [
            ("Under 5'0\"", "short", None, 60),
            ("5'0\" - 5'3\"", "short", 60, 63),
            ("5'4\" - 5'7\"", "average", 64, 67),
            ("5'8\" - 5'11\"", "mixed", 68, 71),
            ("6'0\" - 6'3\"", "tall", 72, 75),
            ("Over 6'3\"", "tall", 75, None),
            ("6 ft 1 in", "tall", 73, 73),
        ]
        for raw, category, lower, upper in cases:
            with self.subTest(raw=raw):
                result = normalize_generation_user_profile({"measurements": {"height": raw}})
                self.assertEqual(result["height"], raw)
                self.assertEqual(result["profileSignals"]["height_category"], category)
                self.assertEqual(result["profileSignals"]["height_range_inches"], {"lower": lower, "upper": upper})

    def test_unknown_optional_values_stay_raw_and_do_not_gain_specific_rules(self):
        source = {"bodyType": "Prefer not to say", "skinTone": "skin_tone_101",
                  "height": "not sure", "weight": "Prefer not to specify"}
        result = normalize_generation_user_profile(source)
        for key, value in source.items():
            self.assertEqual(result[key], value)
        for key in ("body_type", "skin_depth_index", "skin_depth", "skin_undertone", "height_category", "age"):
            self.assertIsNone(result["profileSignals"][key])
        self.assertIsNone(normalize_profile_signals({})["age"])
        self.assertNotIn("age", result)
        self.assertFalse(result["profileSignals"]["plus_size"])

    def test_user_corrections_win_over_nested_values_and_stale_normalized_signals(self):
        source = {"bodyType": "Inverted Triangle", "skinTone": "skin_tone_20", "age": 38,
                  "measurements": {"bodyType": "Round/Apple", "skinTone": "skin_tone_82"},
                  "profileSignals": {"body_type": "apple", "age": 25, "skin_undertone": "warm"}}
        result = normalize_generation_user_profile(source)
        self.assertEqual(result["profileSignals"]["body_type"], "inverted_triangle")
        self.assertEqual(result["profileSignals"]["skin_depth"], "light")
        self.assertIsNone(result["profileSignals"]["skin_undertone"])
        self.assertEqual(result["profileSignals"]["age"], 38)
        self.assertEqual(normalize_generation_user_profile(result), result)

    def test_legacy_depth_and_explicit_undertone_remain_distinct(self):
        self.assertIsNone(normalize_profile_signals({"skinTone": "82"})["skin_undertone"])
        self.assertEqual(normalize_generation_user_profile({"skinTone": 0})["profileSignals"]["skin_depth_index"], 0)
        signals = normalize_profile_signals(SimpleNamespace(skinTone="light cool"))
        self.assertEqual(signals["skin_depth"], "light")
        self.assertEqual(signals["skin_undertone"], "cool")
        self.assertIsNone(signals["skin_depth_index"])

    def test_weight_ranges_do_not_invent_fit_or_plus_size_claims(self):
        for weight in ("201-250 lbs", "251-300 lbs", "Over 300 lbs"):
            self.assertFalse(normalize_profile_signals({"weight": weight})["plus_size"])
        self.assertTrue(normalize_profile_signals({"bodyType": "Plus Size"})["plus_size"])
        for age in (True, "25", float("nan"), float("inf"), -5, 0, 121, 10 ** 1000):
            self.assertIsNone(normalize_profile_signals({"age": age})["age"])


class ActiveProfileAnalyzerTests(unittest.IsolatedAsyncioTestCase):
    """Invoke the real ranking methods with local garments, without generation I/O."""

    def setUp(self):
        from src.services.robust_outfit_generation_service import RobustOutfitGenerationService
        self.service = RobustOutfitGenerationService.__new__(RobustOutfitGenerationService)

    async def score(self, profile, name="Plain shirt", color="white", analyzer="body"):
        item = SimpleNamespace(id="item", name=name, type="shirt", color=color, metadata={},
                               style=[], occasion=[], brand=None)
        scores = {"item": {"item": item}}
        context = SimpleNamespace(user_profile=profile, occasion="Casual", style="Classic",
                                  base_item_id=None, metadata_notes={})
        if analyzer == "body":
            await self.service._analyze_body_type_scores(context, scores)
            return scores["item"]["body_type_score"]
        await self.service._analyze_style_profile_scores(context, scores)
        return scores["item"]["style_profile_score"]

    async def test_quiz_body_aliases_reach_real_rules_from_raw_nested_profile(self):
        self.assertGreater(await self.score({"measurements": {"bodyType": "Round/Apple"}}, "Flowing shirt"),
                           await self.score({}, "Flowing shirt"))
        self.assertGreater(await self.score({"measurements": {"bodyType": "Inverted Triangle"}}, "Simple shirt"),
                           await self.score({}, "Simple shirt"))

    async def test_middle_height_range_does_not_get_short_or_tall_rule(self):
        mixed = {"height": "5'8\" - 5'11\""}
        short = {"height": "5'0\" - 5'3\""}
        tall = {"height": "6'0\" - 6'3\""}
        for name in ("Crop shirt", "Long shirt"):
            self.assertEqual(await self.score(mixed, name), await self.score({}, name))
        self.assertGreater(await self.score(short, "Crop shirt"), await self.score(mixed, "Crop shirt"))
        self.assertGreater(await self.score(tall, "Long shirt"), await self.score(mixed, "Long shirt"))

    async def test_unknown_body_and_weight_do_not_invent_fit_preferences(self):
        self.assertEqual(await self.score({"bodyType": "Prefer not to say"}, "Fitted shirt"),
                         await self.score({}, "Fitted shirt"))
        self.assertEqual(await self.score({"weight": "201-250 lbs"}, "Tailored shirt"),
                         await self.score({}, "Tailored shirt"))
        self.assertGreater(await self.score({"bodyType": "Plus Size"}, "Tailored shirt"),
                           await self.score({}, "Tailored shirt"))

    async def test_slider_depth_reaches_color_ranking_without_warm_or_cool_assumption(self):
        # Emerald is favored by the existing deep palette; coral by warm undertone.
        self.assertGreater(await self.score({"skinTone": "skin_tone_82"}, color="emerald", analyzer="style"),
                           await self.score({}, color="emerald", analyzer="style"))
        self.assertEqual(await self.score({"skinTone": "skin_tone_82"}, color="coral", analyzer="style"),
                         await self.score({}, color="coral", analyzer="style"))
        self.assertGreater(await self.score({"skinTone": "warm"}, color="coral", analyzer="style"),
                           await self.score({"skinTone": "skin_tone_82"}, color="coral", analyzer="style"))
        self.assertEqual(await self.score({"skinTone": "skin_tone_50"}, color="navy", analyzer="style"),
                         await self.score({}, color="navy", analyzer="style"))


if __name__ == "__main__":
    unittest.main()

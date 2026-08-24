import unittest

import numpy as np

from profiles import PROFILES, TravelerProfile, WeightedDistribution
from transition_models import TransitionModel, TransitionModelError


class WeightedDistributionTests(unittest.TestCase):
    def test_rejects_invalid_distributions(self):
        with self.assertRaises(ValueError):
            WeightedDistribution(("a", "b"), (0.4, 0.4))
        with self.assertRaises(ValueError):
            WeightedDistribution(("a", "a"), (0.5, 0.5))
        with self.assertRaises(ValueError):
            WeightedDistribution(("a", "b"), (1.1, -0.1))

    def test_single_value_sampling_is_deterministic(self):
        distribution = WeightedDistribution(("museum",), (1.0,))
        self.assertEqual(
            distribution.sample(np.random.default_rng(42)), "museum"
        )


class TransitionModelTests(unittest.TestCase):
    def test_rejects_invalid_probability_sum(self):
        with self.assertRaises(TransitionModelError):
            TransitionModel(
                {"Start": {"Sleep": 0.5}},
                initial_state="Start",
                terminal_state="Sleep",
            )

    def test_zero_probability_path_does_not_prove_termination(self):
        with self.assertRaises(TransitionModelError):
            TransitionModel(
                {"Start": {"Start": 1.0, "Sleep": 0.0}},
                initial_state="Start",
                terminal_state="Sleep",
            )

    def test_samples_until_terminal(self):
        model = TransitionModel(
            {"Start": {"Visit": 1.0}, "Visit": {"Sleep": 1.0}},
            initial_state="Start",
            terminal_state="Sleep",
        )
        self.assertEqual(
            model.sample(np.random.default_rng(42)),
            ["Start", "Visit", "Sleep"],
        )
        self.assertEqual(
            model.sample(np.random.default_rng(42), include_terminal=False),
            ["Start", "Visit"],
        )


class TravelerProfileTests(unittest.TestCase):
    def test_all_project_profiles_are_valid(self):
        self.assertEqual(len({profile.name for profile in PROFILES}), len(PROFILES))
        for profile in PROFILES:
            self.assertEqual(profile.transition_model.initial_state, "Start")
            self.assertEqual(profile.transition_model.terminal_state, "Sleep")

    def test_nighttime_state_uses_nighttime_preferences(self):
        unit = WeightedDistribution(("Hotel",), (1.0,))
        model = TransitionModel(
            {"Start": {"Sleep": 1.0}},
            initial_state="Start",
            terminal_state="Sleep",
        )
        profile = TravelerProfile(
            name="test",
            transition_model=model,
            accommodation=unit,
            food=WeightedDistribution(("Resto",), (1.0,)),
            activity=WeightedDistribution(("museum",), (1.0,)),
            nighttime=WeightedDistribution(("bar",), (1.0,)),
        )
        rng = np.random.default_rng(42)
        self.assertEqual(profile.sample_category("act_nocturne", rng), "bar")
        self.assertEqual(profile.sample_category("act_matin", rng), "museum")
        self.assertEqual(profile.sample_category("unknown", rng), "act")


if __name__ == "__main__":
    unittest.main()

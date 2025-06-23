from tempfile import NamedTemporaryFile
import numpy as np
import h5py

from django.test import TestCase
from compasui.tests.utils import silence_logging

from publications.utils.h5_functions import (
    get_h5_keys,
    get_h5_subgroups,
    get_h5_subgroup_meta,
    get_h5_subgroup_data,
    get_subgroup_units,
    check_subgroup_boolean,
    remove_null_coords,
)


class TestGetH5Groups(TestCase):
    def setUp(self):
        self.tf = NamedTemporaryFile(suffix=".h5")
        with h5py.File(self.tf, "w") as f:
            f.create_group("/base_group1/subgroup1/")
            f.create_group("/base_group1/subgroup2/")
            f.create_group("/base_group2/subgroup3/")
            f.create_group("/base_group2/subgroup4/")

    def test_get_h5_keys(self):
        with h5py.File(self.tf, "w") as f:
            self.assertSequenceEqual(get_h5_keys(f), ["base_group1", "base_group2"])

    def test_get_h5_subgroups(self):
        with h5py.File(self.tf, "w") as f:
            self.assertSequenceEqual(
                get_h5_subgroups(f, "base_group1"), ["subgroup1", "subgroup2"]
            )
            self.assertSequenceEqual(
                get_h5_subgroups(f, "base_group2"), ["subgroup3", "subgroup4"]
            )


class TestGetH5SubgroupMeta(TestCase):
    def setUp(self):
        self.default_subgroups = {
            "BSE_Common_Envelopes": ["SemiMajorAxis>CE", "SemiMajorAxis<CE"],
            "BSE_Double_Compact_Objects": ["Mass(1)", "Mass(2)"],
            "BSE_System_Parameters": ["Mass@ZAMS(1)", "Mass@ZAMS(2)"],
            "BSE_Supernovae": ["Mass(SN)", "Mass_CO_Core@CO(SN)"],
        }

        self.root_groups = ["test_group", *self.default_subgroups.keys()]

        self.subgroups = [
            "test_dataset_1",
            "test_dataset_2",
            *(val for vals in self.default_subgroups.values() for val in vals),
        ]

        self.tf = NamedTemporaryFile(suffix=".h5")
        with h5py.File(self.tf, "w") as f:
            for root_group in self.root_groups:
                for subgroup in self.subgroups:
                    dataset = f.create_dataset(
                        f"/{root_group}/{subgroup}", data=np.arange(10)
                    )
                    dataset.attrs["units"] = np.bytes_(f"{subgroup}_unit")

            f.create_dataset(
                "/Run_Details/run_details_dataset", data=np.array([1, 2, 3])
            )

    def test_returns_default_data_without_kwargs(self):
        with h5py.File(self.tf, "w") as f:
            meta = get_h5_subgroup_meta(f)
            self.assertSequenceEqual(sorted(meta["groups"]), sorted(self.root_groups))
            self.assertSequenceEqual(sorted(meta["subgroups"]), sorted(self.subgroups))
            self.assertIn(meta["group"], self.root_groups)
            self.assertEqual(
                meta["subgroup_x"],
                self.default_subgroups.get(meta["group"], meta["subgroups"])[0],
            )
            self.assertEqual(
                meta["subgroup_y"],
                self.default_subgroups.get(meta["group"], meta["subgroups"])[1],
            )
            self.assertEqual(meta["subgroup_x_unit"], f'{meta["subgroup_x"]}_unit')
            self.assertEqual(meta["subgroup_y_unit"], f'{meta["subgroup_y"]}_unit')
            self.assertEqual(meta["stride_length"], 1)
            self.assertEqual(meta["total_length"], 10)

    def test_returns_default_subgroups_for_each_root_group(self):
        with h5py.File(self.tf, "w") as f:
            for root_group in self.default_subgroups.keys():
                meta = get_h5_subgroup_meta(f, root_group=root_group)
                self.assertEqual(meta["group"], root_group)
                self.assertEqual(
                    meta["subgroup_x"], self.default_subgroups[meta["group"]][0]
                )
                self.assertEqual(
                    meta["subgroup_y"], self.default_subgroups[meta["group"]][1]
                )
                self.assertEqual(meta["subgroup_x_unit"], f'{meta["subgroup_x"]}_unit')
                self.assertEqual(meta["subgroup_y_unit"], f'{meta["subgroup_y"]}_unit')

    def test_returns_first_subgroups_if_unknown_root_group(self):
        with h5py.File(self.tf, "w") as f:
            meta = get_h5_subgroup_meta(f, root_group="test_group")
            self.assertEqual(meta["group"], "test_group")
            self.assertEqual(meta["subgroup_x"], meta["subgroups"][0])
            self.assertEqual(meta["subgroup_y"], meta["subgroups"][1])
            self.assertEqual(meta["subgroup_x_unit"], f'{meta["subgroup_x"]}_unit')
            self.assertEqual(meta["subgroup_y_unit"], f'{meta["subgroup_y"]}_unit')

    def test_returns_subgroups_if_specified(self):
        with h5py.File(self.tf, "w") as f:
            meta = get_h5_subgroup_meta(
                f, root_group="test_group", subgroup_x="Mass(1)", subgroup_y="Mass(2)"
            )
            self.assertEqual(meta["group"], "test_group")
            self.assertEqual(meta["subgroup_x"], "Mass(1)")
            self.assertEqual(meta["subgroup_y"], "Mass(2)")
            self.assertEqual(meta["subgroup_x_unit"], f'{meta["subgroup_x"]}_unit')
            self.assertEqual(meta["subgroup_y_unit"], f'{meta["subgroup_y"]}_unit')

    def test_returns_stride_length_if_specified(self):
        with h5py.File(self.tf, "w") as f:
            meta = get_h5_subgroup_meta(f, stride_length=2)
            self.assertEqual(meta["stride_length"], 2)


class TestGetH5SubgroupData(TestCase):
    def setUp(self):
        self.tf = NamedTemporaryFile(suffix=".h5")
        with h5py.File(self.tf, "w") as f:
            test_dataset = f.create_dataset(
                "/base_group/test_dataset",
                data=np.array([10, 10, 10, 10, 20, 30], dtype=np.uint32),
            )
            test_dataset.attrs["units"] = np.bytes_("test_unit")

            f.create_dataset(
                "/base_group/string_dataset", data=np.array([b"string_type"])
            )

    @silence_logging(logger_name="publications.utils.h5_functions")
    def test_returns_none_if_string_type(self):
        with h5py.File(self.tf, "w") as f:
            self.assertIsNone(
                get_h5_subgroup_data(f, "base_group", "string_dataset", "test_dataset")
            )
            self.assertIsNone(
                get_h5_subgroup_data(f, "base_group", "test_dataset", "string_dataset")
            )

    def test_returns_data(self):
        with h5py.File(self.tf, "w") as f:
            self.assertDictEqual(
                get_h5_subgroup_data(f, "base_group", "test_dataset", "test_dataset"),
                {
                    "sides": [0.5, 0.5],
                    "hist_data": '[{"x": 10.0, "y": 10.0, "counts": 4.0}]',
                    "scatter_data": '[{"x": 20.0, "y": 20.0}, {"x": 30.0, "y": 30.0}]',
                    "min_max_x": [10.0, 30.0],
                    "min_max_y": [10.0, 30.0],
                    "null_check_x": False,
                    "null_check_y": False,
                    "log_check_x": False,
                    "log_check_y": False,
                    "bool_check_x": False,
                    "bool_check_y": False,
                },
            )


class TestGetH5SubgroupMethods(TestCase):
    def setUp(self):
        self.tf = NamedTemporaryFile(suffix=".h5")
        with h5py.File(self.tf, "w") as f:
            int_dataset = f.create_dataset(
                "/base_group/int_dataset", data=np.arange(10, dtype=np.uint32)
            )
            int_dataset.attrs["units"] = np.bytes_("int_unit")

            float_dataset = f.create_dataset(
                "/base_group/float_dataset", data=np.arange(10, dtype=np.float32)
            )
            float_dataset.attrs["units"] = np.bytes_("float_unit")

            state_dataset = f.create_dataset(
                "/base_group/state_dataset", data=np.arange(10, dtype=np.uint32)
            )
            state_dataset.attrs["units"] = np.bytes_("State")

            event_dataset = f.create_dataset(
                "/base_group/event_dataset", data=np.arange(10, dtype=np.uint32)
            )
            event_dataset.attrs["units"] = np.bytes_("Event")

            unitless_dataset = f.create_dataset(
                "/base_group/unitless_dataset", data=np.arange(10, dtype=np.uint32)
            )
            unitless_dataset.attrs["units"] = np.bytes_("-")

            bool_dataset = f.create_dataset(
                "/base_group/bool_dataset", data=np.array([0, 1, 0, 1], dtype=np.uint8)
            )
            bool_dataset.attrs["units"] = np.bytes_("State")

            f.create_dataset(
                "/base_group/string_dataset", data=np.array([b"string_type"])
            )

    def test_get_units(self):
        with h5py.File(self.tf, "w") as f:
            self.assertEqual(
                get_subgroup_units(f, "base_group", "int_dataset"), "int_unit"
            )
            self.assertEqual(
                get_subgroup_units(f, "base_group", "float_dataset"), "float_unit"
            )
            self.assertEqual(get_subgroup_units(f, "base_group", "state_dataset"), None)
            self.assertEqual(get_subgroup_units(f, "base_group", "event_dataset"), None)
            self.assertEqual(
                get_subgroup_units(f, "base_group", "unitless_dataset"), None
            )

    def test_bool_check(self):
        with h5py.File(self.tf, "w") as f:
            self.assertFalse(check_subgroup_boolean(f, "base_group", "int_dataset"))
            self.assertFalse(check_subgroup_boolean(f, "base_group", "float_dataset"))
            self.assertFalse(check_subgroup_boolean(f, "base_group", "state_dataset"))
            self.assertTrue(check_subgroup_boolean(f, "base_group", "bool_dataset"))


class TestRemoveNullCoords(TestCase):
    def test_remove_null_coords(self):
        arr1 = np.array([np.nan, 1, 2, 3, np.nan, 5])
        arr2 = np.array([np.nan, 5, 4, 3, 2, np.nan])
        new_arr1, new_arr2 = remove_null_coords(arr1, arr2)
        self.assertSequenceEqual(new_arr1.tolist(), [1, 2, 3])
        self.assertSequenceEqual(new_arr2.tolist(), [5, 4, 3])

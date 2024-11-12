from tempfile import NamedTemporaryFile
import numpy as np
import h5py

from django.test import TestCase

from publications.utils.h5_functions import (
    get_h5_keys,
    get_h5_subgroups,
    get_h5_subgroup_data,
    get_subgroup_units,
    check_subgroup_boolean,
    remove_null_coords,
)


class TestGetH5Groups(TestCase):
    def setUp(self):
        self.tf = NamedTemporaryFile(suffix='.h5')
        with h5py.File(self.tf, 'w') as f:
            f.create_group('/base_group1/subgroup1/')
            f.create_group('/base_group1/subgroup2/')
            f.create_group('/base_group2/subgroup3/')
            f.create_group('/base_group2/subgroup4/')

    def test_get_h5_keys(self):
        with h5py.File(self.tf, 'w') as f:
            self.assertSequenceEqual(get_h5_keys(f), ['base_group1', 'base_group2'])

    def test_get_h5_subgroups(self):
        with h5py.File(self.tf, 'w') as f:
            self.assertSequenceEqual(get_h5_subgroups(f, 'base_group1'), ['subgroup1', 'subgroup2'])
            self.assertSequenceEqual(get_h5_subgroups(f, 'base_group2'), ['subgroup3', 'subgroup4'])


class TestGetH5SubgroupMethods(TestCase):
    def setUp(self):
        self.tf = NamedTemporaryFile(suffix='.h5')
        with h5py.File(self.tf, 'w') as f:
            int_dataset = f.create_dataset('/base_group/int_dataset', data=np.arange(10, dtype=np.uint32))
            int_dataset.attrs['units'] = np.bytes_('int_unit')

            float_dataset = f.create_dataset('/base_group/float_dataset', data=np.arange(10, dtype=np.float32))
            float_dataset.attrs['units'] = np.bytes_('float_unit')
            
            state_dataset = f.create_dataset('/base_group/state_dataset', data=np.arange(10, dtype=np.uint32))
            state_dataset.attrs['units'] = np.bytes_('State')

            event_dataset = f.create_dataset('/base_group/event_dataset', data=np.arange(10, dtype=np.uint32))
            event_dataset.attrs['units'] = np.bytes_('Event')

            unitless_dataset = f.create_dataset('/base_group/unitless_dataset', data=np.arange(10, dtype=np.uint32))
            unitless_dataset.attrs['units'] = np.bytes_('-')

            bool_dataset = f.create_dataset('/base_group/bool_dataset', data=np.array([0, 1, 0, 1], dtype=np.uint8))
            bool_dataset.attrs['units'] = np.bytes_('State')

            f.create_dataset('/base_group/string_dataset', data=np.array([b'string_type']))

    def test_h5_data_returns_none_if_string(self):
        with h5py.File(self.tf, 'w') as f:
            self.assertIsNone(get_h5_subgroup_data(f, 'base_group', 'string_dataset', 'int_dataset'))

    def test_get_units(self):
        with h5py.File(self.tf, 'w') as f:
            self.assertEqual(get_subgroup_units(f, 'base_group', 'int_dataset'), 'int_unit')
            self.assertEqual(get_subgroup_units(f, 'base_group', 'float_dataset'), 'float_unit')
            self.assertEqual(get_subgroup_units(f, 'base_group', 'state_dataset'), None)
            self.assertEqual(get_subgroup_units(f, 'base_group', 'event_dataset'), None)
            self.assertEqual(get_subgroup_units(f, 'base_group', 'unitless_dataset'), None)

    def test_bool_check(self):
        with h5py.File(self.tf, 'w') as f:
            self.assertFalse(check_subgroup_boolean(f, 'base_group', 'int_dataset'))
            self.assertFalse(check_subgroup_boolean(f, 'base_group', 'float_dataset'))
            self.assertFalse(check_subgroup_boolean(f, 'base_group', 'state_dataset'))
            self.assertTrue(check_subgroup_boolean(f, 'base_group', 'bool_dataset'))


class TestRemoveNullCoords(TestCase):
    def test_remove_null_coords(self):
        arr1 = np.array([np.nan, 1, 2, 3, np.nan, 5])
        arr2 = np.array([np.nan, 5, 4, 3, 2, np.nan])
        new_arr1, new_arr2 = remove_null_coords(arr1, arr2)
        self.assertSequenceEqual(new_arr1.tolist(), [1, 2, 3])
        self.assertSequenceEqual(new_arr2.tolist(), [5, 4, 3])

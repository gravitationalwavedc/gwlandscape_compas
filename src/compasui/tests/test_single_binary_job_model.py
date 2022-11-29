from django.test import testcases, override_settings
from tempfile import TemporaryDirectory
from pathlib import Path
from django.conf import settings
from compasui.models import SingleBinaryJob

temp_output_dir = TemporaryDirectory()


@override_settings(COMPAS_IO_PATH=temp_output_dir.name)
class TestSingleBinaryJobModel(testcases.TestCase):
    def test_create_with_defaults(self):
        job = SingleBinaryJob(
            mass1=1.5,
            mass2=1.51,
            metallicity=0.02,
            eccentricity=0.1,
            separation=0.1
        )
        expected_gridfiletext = "--initial-mass-1 1.5 --initial-mass-2 1.51 --metallicity 0.02 --eccentricity 0.1 " \
                                "--semi-major-axis 0.1 --kick-magnitude-1 0.0 --kick-magnitude-2 0.0 " \
                                "--common-envelope-alpha 1.0 --common-envelope-lambda-prescription LAMBDA_NANJING " \
                                "--remnant-mass-prescription FRYER2012 --fryer-supernova-engine DELAYED " \
                                "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC " \
                                "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 "

        job.save()
        self.assertEqual(job.bse_grid_content, expected_gridfiletext)

    def test_create_with_null_values(self):
        job = SingleBinaryJob(
            mass1=1.5,
            mass2=1.51,
            metallicity=0.02,
            eccentricity=0.1,
            separation=0.1,
            orbital_period=None,
            fryer_supernova_engine=None
        )

        expected_gridfiletext = "--initial-mass-1 1.5 --initial-mass-2 1.51 --metallicity 0.02 --eccentricity 0.1 " \
                                "--semi-major-axis 0.1 --kick-magnitude-1 0.0 --kick-magnitude-2 0.0 " \
                                "--common-envelope-alpha 1.0 --common-envelope-lambda-prescription LAMBDA_NANJING " \
                                "--remnant-mass-prescription FRYER2012 " \
                                "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC " \
                                "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 "

        job.save()
        self.assertEqual(job.bse_grid_content, expected_gridfiletext)

    def test_create_with_orbital_value_provided(self):
        job = SingleBinaryJob(
            mass1=1.5,
            mass2=1.51,
            metallicity=0.02,
            eccentricity=0.1,
            separation=0.1,
            orbital_period=0.12
        )

        expected_gridfiletext = "--initial-mass-1 1.5 --initial-mass-2 1.51 --metallicity 0.02 --eccentricity 0.1 " \
                                "--semi-major-axis 0.1 --orbital-period 0.12 --kick-magnitude-1 0.0 " \
                                "--kick-magnitude-2 0.0 " \
                                "--common-envelope-alpha 1.0 --common-envelope-lambda-prescription LAMBDA_NANJING " \
                                "--remnant-mass-prescription FRYER2012 --fryer-supernova-engine DELAYED " \
                                "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC " \
                                "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 "

        job.save()
        self.assertEqual(job.bse_grid_content, expected_gridfiletext)

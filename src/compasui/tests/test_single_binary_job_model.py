from django.test import testcases, override_settings
from tempfile import TemporaryDirectory
from pathlib import Path
from django.conf import settings
from compasui.models import SingleBinaryJob


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestSingleBinaryJobModel(testcases.TestCase):

    def grid_file_is_created_successfully(self, job_id, expected_text):
        grid_file_path = Path(f'{settings.MEDIA_ROOT}/jobs/{job_id}/BSE_grid.txt')
        self.assertEqual(SingleBinaryJob.objects.count(), 1)
        self.assertTrue(grid_file_path.exists())
        with open(grid_file_path) as f:
            content = f.read()
            self.assertEqual(content, expected_text)

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
                                "--common-envelope-lambda 0.1 --remnant-mass-prescription FRYER2012 " \
                                "--fryer-supernova-engine DELAYED --black-hole-kicks FALLBACK " \
                                "--kick-magnitude-sigma-CCSN-NS 250.0 --kick-magnitude-sigma-CCSN-BH 256.0 " \
                                "--kick-magnitude-sigma-ECSN 30.0 --kick-magnitude-sigma-USSN 30.0 " \
                                "--pisn-lower-limit 60.0 --pisn-upper-limit 135.0 --ppi-lower-limit 35.0 " \
                                "--ppi-upper-limit 60.0 " \
                                "--pulsational-pair-instability-prescription MARCHANT " \
                                "--maximum-neutron-star-mass 3.0 " \
                                "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC " \
                                "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 " \
                                "--mass-transfer-jloss 1.0 "
        job.save()
        self.grid_file_is_created_successfully(job.id, expected_gridfiletext)

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
                                "--common-envelope-lambda 0.1 --remnant-mass-prescription FRYER2012 " \
                                "--black-hole-kicks FALLBACK " \
                                "--kick-magnitude-sigma-CCSN-NS 250.0 --kick-magnitude-sigma-CCSN-BH 256.0 " \
                                "--kick-magnitude-sigma-ECSN 30.0 " \
                                "--kick-magnitude-sigma-USSN 30.0 --pisn-lower-limit 60.0 " \
                                "--pisn-upper-limit 135.0 --ppi-lower-limit 35.0 --ppi-upper-limit 60.0 " \
                                "--pulsational-pair-instability-prescription MARCHANT " \
                                "--maximum-neutron-star-mass 3.0 " \
                                "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC " \
                                "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 " \
                                "--mass-transfer-jloss 1.0 "
        job.save()
        self.grid_file_is_created_successfully(job.id, expected_gridfiletext)

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
                                "--kick-magnitude-2 0.0 --common-envelope-alpha 1.0 " \
                                "--common-envelope-lambda-prescription LAMBDA_NANJING " \
                                "--common-envelope-lambda 0.1 --remnant-mass-prescription FRYER2012 " \
                                "--fryer-supernova-engine DELAYED --black-hole-kicks FALLBACK " \
                                "--kick-magnitude-sigma-CCSN-NS 250.0 --kick-magnitude-sigma-CCSN-BH 256.0 " \
                                "--kick-magnitude-sigma-ECSN 30.0 --kick-magnitude-sigma-USSN 30.0 " \
                                "--pisn-lower-limit 60.0 --pisn-upper-limit 135.0 --ppi-lower-limit 35.0 " \
                                "--ppi-upper-limit 60.0 " \
                                "--pulsational-pair-instability-prescription MARCHANT " \
                                "--maximum-neutron-star-mass 3.0 " \
                                "--mass-transfer-angular-momentum-loss-prescription ISOTROPIC " \
                                "--mass-transfer-accretion-efficiency-prescription THERMAL --mass-transfer-fa 0.5 " \
                                "--mass-transfer-jloss 1.0 "
        job.save()
        self.grid_file_is_created_successfully(job.id, expected_gridfiletext)


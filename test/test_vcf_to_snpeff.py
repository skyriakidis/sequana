# Import -----------------------------------------------------------------------

import os
import shutil
from sequana import vcf_to_snpeff
from easydev import TempFile
from . import data
pathdata = data.__path__[0]

# Test -------------------------------------------------------------------------

def test_vcf_to_snpeff():

    mydata = vcf_to_snpeff.VCFToSnpeff(
            vcf_filename=pathdata + os.sep + "test.vcf",
            reference=pathdata + os.sep + "test.gb")
    mydata = vcf_to_snpeff.VCFToSnpeff(
            vcf_filename=pathdata + os.sep + "test.vcf",
            reference="Bordetella_pertussis_Tohama_I_uid57617")
    with TempFile() as fh:
        mydata.launch_snpeff(fh.name)

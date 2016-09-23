cd /home/sequana

apt-get update
apt-get install wget -y 
apt-get install bzip2 -y
apt-get -y install gcc # required to compile the cython code
apt-get install libxtst6 -y
apt-get install -y python-qt4
apt-get install git -y

apt-get install libpng-dev -y
apt-get install zlib1g-dev -y
apt-get install make -y
apt-get install xvfb -y

wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod 755 Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b -f -p miniconda3

source miniconda3/bin/activate

conda config --add channels r
conda config --add channels bioconda

conda install numpy matplotlib pandas cutadapt pysam pyvcf snpeff -y
conda install snakemake biokit bioservices spades khmer -y
conda install bwa bcftools samtools==1.3.0 bedtools picard freebayes fastqc -y
conda install kraken krona scipy  graphviz -y

conda install ipython -y

# Finally, Sequana release itself
pip install sequana==0.1.11

#git clone https://github.com/sequana/sequana

#
cp miniconda3/lib/python3.5/site-packages/sequana/resources/data/Hm2_GTGAAA_L005_R* .
cp miniconda3/lib/python3.5/site-packages/sequana/resources/data/virus.bed  .

# test
# sequana_coverage --input virus.bed
# sequana --pipeline quality --file1 --file2
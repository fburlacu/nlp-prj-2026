#!/bin/bash
#SBATCH -p students
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32gb
#SBATCH --time=8:00:00

module load anaconda3/2025.06
source activate nlp-prj
cd "$SLURM_SUBMIT_DIR"

python main.py --retriever dense

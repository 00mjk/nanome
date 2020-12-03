#!/home/liuya/anaconda3/envs/nmf/bin/python
import glob
import logging
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

nanocompare_prj = "/projects/li-lab/yang/workspace/nano-compare/src"
sys.path.append(nanocompare_prj)

from global_config import set_log_debug_level, pic_base_dir

"""
Sample file:

head K562_WGBS_Joined-meth-cov-DeepMod-baseCount0.bed
chr1	2177309	2177310	0.75	4	-
chr1	2177329	2177330	0.5	4	-
chr1	2177539	2177540	0.25	4	-
chr1	2177652	2177653	0.5	4	-
chr1	2177725	2177726	0.5	4	-
chr1	2177773	2177774	0.25	4	-
chr1	2177909	2177910	0.5	4	-
chr1	2177946	2177947	0.25	4	-
chr1	2178202	2178203	0.25	4	-
chr1	2178228	2178229	0.25	4	-

head K562_WGBS_Joined-meth-cov-DeepMod-bgtruth-closest.bed
chr1	2177309	2177310	0.75	4	-	chr1	2177308	2177309	1.0	17	-	1
chr1	2177329	2177330	0.5	4	-	chr1	2177328	2177329	0.893157894736842	19	-	1
chr1	2177539	2177540	0.25	4	-	chr1	2177538	2177539	0.9737500000000001	40	-	1
chr1	2177652	2177653	0.5	4	-	chr1	2177651	2177652	0.9637931034482758	30	-	1
chr1	2177725	2177726	0.5	4	-	chr1	2177724	2177725	0.7933333333333333	25	-	1
chr1	2177773	2177774	0.25	4	-	chr1	2177769	2177770	0.7715384615384616	29	-	4
chr1	2177909	2177910	0.5	4	-	chr1	2177908	2177909	1.0	30	-	1
chr1	2177946	2177947	0.25	4	-	chr1	2177948	2177949	0.7012547	-	2
chr1	2178202	2178203	0.25	4	-	chr1	2178189	2178190	0.59	66	-	13
chr1	2178228	2178229	0.25	4	-	chr1	2178232	2178233	0.9249056603773584	55	-	4
"""

colnames = ['chr-1', 'start-1', 'end-1', 'meth-freq-1', 'cov-1', 'strand-1'] + \
           ['chr-2', 'start-2', 'end-2', 'meth-freq-2', 'cov-2', 'strand-2'] + ['nearest-dist']

dtypes = [str, np.int64, np.int64, np.float64, np.int64, str] + \
         [str, np.int64, np.int64, np.float64, np.int64, str] + [np.int64]

dtype_dict = {col: dt for col, dt in zip(colnames, dtypes)}

fn_base_dir = '/projects/li-lab/yang/workspace/nano-compare/src/nanocompare/bedtools'


def load_df(infn):
    """
    Load the infile for closest operation of two bed files
    :param infn:
    :return:
    """

    # infn = os.path.join(fn_base_dir, infn)
    df = pd.read_csv(infn, sep='\t', header=None, dtype=dtype_dict)
    df.columns = colnames
    df['meth-freq-2'] = df['meth-freq-2'].replace('.', '0.0').astype(np.float64)
    # logging.debug(df)
    # logging.info(df.dtypes)
    return df


def plot_hist_of_df(infn, nearest_cutoff=10, nearest_col=-1):
    """
    Plot the histogram of closest results (Nereast CpGs sites)
    :param infn:
    :param nearest_cutoff:
    :return:
    """
    title = os.path.basename(infn).replace(".bed", '').replace('meth-cov-', '').replace('-bgtruth-closest', '')

    df = load_df(infn=infn)

    data = df.iloc[:, nearest_col]
    data = data[data <= nearest_cutoff]
    # data = data[data >= 0]  # remove -1, due to no occurrance in bg-truth

    vc = data.value_counts()
    vc = vc.sort_index()

    outfn = os.path.join(pic_base_dir, f'hist-data-{title}.csv')
    vc.to_csv(outfn)
    logging.debug(vc)

    num_bins = len(vc)
    min_x = min(vc.index)
    min_x = 0
    logging.debug(f'min_x={min_x}, num_bins={num_bins}')

    plt.figure(figsize=(4, 3))

    ax = sns.histplot(data=data, stat='probability', bins=num_bins, discrete=True)  # discrete=True,

    # ax.set_xlim(min_x, nearest_cutoff)
    # ax.set_xticklabels(list(range(nearest_cutoff + 1)))
    ax.set_xticks(list(range(nearest_cutoff + 1)))
    ax.set_title(title)
    ax.set_xlabel('Nearest distances by closest')

    # mids = [rect.get_x() + rect.get_width() / 2 for rect in ax.patches]
    # ax.set_xticks(mids)
    # if min_x == 0:
    #     ax.set_xticklabels(list(range(nearest_cutoff + 1)))
    # else:
    #     ax.set_xticklabels([-1] + list(range(nearest_cutoff + 1)))

    # sns.displot(df, x="nearest-dist")
    outfn = os.path.join(pic_base_dir, f'dist-plot-{os.path.basename(infn)}.png')
    plt.savefig(outfn, dpi=600, bbox_inches='tight', format="png")
    logging.info(f"save to {outfn}")

    plt.show()
    plt.close()


if __name__ == '__main__':
    set_log_debug_level()

    fnlist = glob.glob(f"{fn_base_dir}/*closest.bed")

    for fn in fnlist:
        plot_hist_of_df(infn=fn)
